using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;

namespace DC2DMMesTextTool
{
    public class MesToolProcessor
    {
        private static readonly Encoding ShiftJIS;
        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            WriteIndented = true,
            Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
        };

        static MesToolProcessor()
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            ShiftJIS = Encoding.GetEncoding(932);
        }

        public event Action<string> Log;

        private void LogMessage(string message)
        {
            Log?.Invoke(message);
        }

        private void LogError(string message)
        {
            Log?.Invoke($"Error: {message}");
        }

        public int ExportMesToJson(string inputPath, string outputPath)
        {
            LogMessage($"Exporting {Path.GetFileName(inputPath)}... ");
            
            try
            {
                var script = new MesScript();
                script.Load(inputPath);
                
                var entries = script.ExtractText(ShiftJIS);
                
                if (entries.Count < 5)
                {
                    var patternEntries = script.ExtractTextPatternBased(ShiftJIS);
                    if (patternEntries.Count > entries.Count)
                        entries = patternEntries;
                }
                
                var processedEntries = ProcessEntries(entries);
                
                string json = JsonSerializer.Serialize(processedEntries, JsonOptions);
                File.WriteAllText(outputPath, json, Encoding.UTF8);
                
                LogMessage($"OK ({processedEntries.Count} entries)");
                return 0;
            }
            catch (Exception ex)
            {
                LogError($"Failed to export {inputPath}: {ex.Message}");
                return 1;
            }
        }

        private List<TextEntry> ProcessEntries(List<TextEntry> entries)
        {
            var processed = new List<TextEntry>(entries.Count);

            for (int i = 0; i < entries.Count; i++)
            {
                var current = entries[i];

                // DC2DM stores a speaker name and its spoken line as two
                // consecutive text entries in the MES bytecode. Present that
                // pair as one conventional JSON dialogue object:
                // { "name": "Otome", "message": "「...」" }
                if (i + 1 < entries.Count &&
                    IsLikelySpeakerName(current.Message) &&
                    IsDialogue(entries[i + 1].Message))
                {
                    var dialogue = entries[++i];
                    processed.Add(new TextEntry
                    {
                        Name = current.Message.Trim(),
                        Message = dialogue.Message,
                        Offset = dialogue.Offset,
                        OriginalLength = dialogue.OriginalLength,
                        Opcode = dialogue.Opcode,
                        IsEncrypted = dialogue.IsEncrypted,
                        IsChoice = dialogue.IsChoice
                    });
                    continue;
                }

                processed.Add(current);
            }

            return processed;
        }

        private static bool IsDialogue(string? text)
        {
            if (string.IsNullOrWhiteSpace(text))
                return false;

            string value = text.TrimStart();
            return value.StartsWith("「", StringComparison.Ordinal) ||
                   value.StartsWith("『", StringComparison.Ordinal) ||
                   value.StartsWith("“", StringComparison.Ordinal);
        }

        private static bool IsLikelySpeakerName(string? text)
        {
            if (string.IsNullOrWhiteSpace(text))
                return false;

            string value = text.Trim();

            // Names in this engine are short, single-line labels. These
            // guards prevent a narration sentence from being consumed as a
            // name merely because the next entry happens to be dialogue.
            if (value.Length > 40 || value.Contains('\n') || value.Contains('\r'))
                return false;

            if (IsDialogue(value))
                return false;

            // Anonymous/uncertain nameplates are used by DC2DM before a
            // character identity is revealed (for example "？？？" or
            // "Otome？"). Treat the trailing question mark as part of the
            // nameplate, while still rejecting sentence-like punctuation.
            if (value.All(c => c == '?' || c == '？'))
                return true;

            string nameForValidation = value.TrimEnd('?', '？');
            if (nameForValidation.Length == 0)
                return false;

            char[] sentenceMarkers =
            {
                '.', ',', ':', ';', '!',
                '。', '、', '，', '：', '；', '！', '…',
                '「', '」', '『', '』', '“', '”'
            };

            if (nameForValidation.IndexOfAny(sentenceMarkers) >= 0 ||
                nameForValidation.Contains('?') ||
                nameForValidation.Contains('？'))
                return false;

            int wordCount = nameForValidation.Split(' ', StringSplitOptions.RemoveEmptyEntries).Length;
            return wordCount <= 5;
        }

        public int NormalizeJsonFolder(string folderPath, string? backupFolder = null)
        {
            if (!Directory.Exists(folderPath))
            {
                LogError($"JSON folder not found: {folderPath}");
                return 1;
            }

            string[] jsonFiles = Directory.GetFiles(folderPath, "*.json");
            if (jsonFiles.Length == 0)
            {
                LogMessage("No JSON files found.");
                return 0;
            }

            backupFolder ??= folderPath.TrimEnd(Path.DirectorySeparatorChar) +
                "_backup_before_dialog_merge_" + DateTime.Now.ToString("yyyyMMdd_HHmmss");
            Directory.CreateDirectory(backupFolder);

            int changedFiles = 0;
            int mergedPairs = 0;

            foreach (string jsonPath in jsonFiles)
            {
                string json = File.ReadAllText(jsonPath, Encoding.UTF8);
                var entries = JsonSerializer.Deserialize<List<TextEntry>>(json)
                    ?? new List<TextEntry>();
                var processed = ProcessEntries(entries);
                int mergedInFile = entries.Count - processed.Count;

                File.Copy(jsonPath, Path.Combine(backupFolder, Path.GetFileName(jsonPath)), true);

                if (mergedInFile <= 0)
                    continue;

                string temporaryPath = jsonPath + ".dialog-merge.tmp";
                string normalizedJson = JsonSerializer.Serialize(processed, JsonOptions);
                File.WriteAllText(temporaryPath, normalizedJson, new UTF8Encoding(false));
                _ = JsonSerializer.Deserialize<List<TextEntry>>(
                    File.ReadAllText(temporaryPath, Encoding.UTF8))
                    ?? throw new InvalidDataException("Normalized JSON validation failed.");
                File.Move(temporaryPath, jsonPath, true);
                changedFiles++;
                mergedPairs += mergedInFile;
            }

            LogMessage($"Normalized {changedFiles}/{jsonFiles.Length} files; merged {mergedPairs} speaker/dialogue pairs.");
            LogMessage($"Backup: {backupFolder}");
            return 0;
        }

        public int ImportJsonToMes(string jsonPath, string originalMesPath, string outputPath, int wrapWidth = TextFormatter.DefaultWrapWidth)
        {
            LogMessage($"Importing {Path.GetFileName(jsonPath)}... ");
            
            try
            {
                string json = File.ReadAllText(jsonPath, Encoding.UTF8);
                var entries = JsonSerializer.Deserialize<List<TextEntry>>(json) 
                    ?? new List<TextEntry>();
                
                if (wrapWidth < 10 || wrapWidth > TextFormatter.DefaultWrapWidth)
                    throw new ArgumentOutOfRangeException(nameof(wrapWidth), "DC2DM dialogue/backlog wrap width must be 10..46.");
                // Also accept legacy JSON with separate speaker/message entries.
                entries = ProcessEntries(entries);
                var expandedEntries = new List<TextEntry>();
                foreach (var entry in entries)
                {
                    if (!string.IsNullOrEmpty(entry.Name))
                    {
                        expandedEntries.Add(new TextEntry
                        {
                            Message = entry.Name.Trim(),
                            IsNameplate = true
                        });
                    }
                    expandedEntries.Add(new TextEntry { Message = entry.Message });
                }
                
                var script = new MesScript();
                script.Load(originalMesPath);

                int originalEntryCount = script.ExtractText(ShiftJIS).Count;
                if (expandedEntries.Count != originalEntryCount)
                {
                    throw new InvalidDataException(
                        $"JSON expands to {expandedEntries.Count} MES text entries, " +
                        $"but the original MES contains {originalEntryCount}. " +
                        "Do not add/remove dialogue objects or name fields.");
                }
                
                var formatter = new TextFormatter { MaxLineLength = wrapWidth };
                byte[] newMes = script.ImportText(expandedEntries, ShiftJIS, formatter);
                File.WriteAllBytes(outputPath, newMes);
                
                LogMessage($"OK ({entries.Count} entries -> {expandedEntries.Count} expanded)");
                return 0;
            }
            catch (Exception ex)
            {
                LogError($"Failed to import {jsonPath}: {ex.Message}");
                return 1;
            }
        }

        public int BatchExport(string inputFolder, string outputFolder)
        {
            if (!Directory.Exists(inputFolder))
            {
                LogError($"Folder not found: {inputFolder}");
                return 1;
            }

            Directory.CreateDirectory(outputFolder);
            var mesFiles = Directory.GetFiles(inputFolder, "*.mes");
            LogMessage($"Found {mesFiles.Length} MES files in {inputFolder}");

            int success = 0;
            int failed = 0;

            foreach (var mesFile in mesFiles)
            {
                string outputPath = Path.Combine(outputFolder, Path.GetFileNameWithoutExtension(mesFile) + ".json");
                if (ExportMesToJson(mesFile, outputPath) == 0)
                    success++;
                else
                    failed++;
            }
            
            LogMessage($"Batch Export Completed: {success} success, {failed} failed");
            return failed > 0 ? 1 : 0;
        }

        public int BatchImport(string jsonFolder, string mesFolder, string outputFolder, int wrapWidth)
        {
            if (!Directory.Exists(jsonFolder))
            {
                LogError($"JSON folder not found: {jsonFolder}");
                return 1;
            }
            
            if (!Directory.Exists(mesFolder))
            {
                LogError($"MES folder not found: {mesFolder}");
                return 1;
            }

            Directory.CreateDirectory(outputFolder);
            var jsonFiles = Directory.GetFiles(jsonFolder, "*.json");
            LogMessage($"Found {jsonFiles.Length} JSON files (wrap width: {wrapWidth})");

            int success = 0;
            int failed = 0;

            foreach (var jsonFile in jsonFiles)
            {
                string baseName = Path.GetFileNameWithoutExtension(jsonFile);
                string mesFile = Path.Combine(mesFolder, baseName + ".mes");
                string outputPath = Path.Combine(outputFolder, baseName + ".mes");
                
                if (!File.Exists(mesFile))
                {
                    LogMessage($"Skipping {baseName} - original MES not found");
                    continue;
                }
                
                if (ImportJsonToMes(jsonFile, mesFile, outputPath, wrapWidth) == 0)
                    success++;
                else
                    failed++;
            }

            LogMessage($"Batch Import Completed: {success} success, {failed} failed");
            return failed > 0 ? 1 : 0;
        }
    }
}
