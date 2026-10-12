using DC2DMMesTextTool;
using System.Text.Json;

// Use a real MES bytecode template and separate test outputs, never live scripts.
string template = Path.GetFullPath(args[0]);
string output = Path.GetFullPath(args[1]);
Directory.CreateDirectory(output);
var processor = new MesToolProcessor();
var logs = new List<string>();
processor.Log += logs.Add;
int checks = 0;
void Check(bool ok, string message)
{
    checks++;
    if (!ok) throw new Exception(message + "\n" + string.Join("\n", logs));
}
List<TextEntry> Read(string path) => JsonSerializer.Deserialize<List<TextEntry>>(File.ReadAllText(path))!;
void Write(string path, List<TextEntry> entries) => File.WriteAllText(path, JsonSerializer.Serialize(entries));
var formatter = new TextFormatter();
// A different game's MES must fail before replacing an existing output.
byte[] templateBytes = File.ReadAllBytes(template);
int versionOffset = BitConverter.ToInt32(templateBytes, 0) * 6 + 4;
foreach (ushort unsupportedVersion in new ushort[] { 0x9872, 0xAAB6, 0xABB6 }) {
    byte[] unsupportedBytes = (byte[])templateBytes.Clone();
    BitConverter.GetBytes(unsupportedVersion).CopyTo(unsupportedBytes, versionOffset);
    string unsupportedMes = Path.Combine(output, $"unsupported_{unsupportedVersion:X4}.mes");
    string preservedJson = Path.Combine(output, $"unsupported_{unsupportedVersion:X4}.json");
    File.WriteAllBytes(unsupportedMes, unsupportedBytes);
    File.WriteAllText(preservedJson, "preserve existing output");
    Check(processor.ExportMesToJson(unsupportedMes, preservedJson) != 0, "Reject unsupported MES version");
    Check(File.ReadAllText(preservedJson) == "preserve existing output", "Unsupported input preserves output");
}
foreach (int invalidCount in new[] { -1, int.MaxValue }) {
    byte[] invalidHeader = (byte[])templateBytes.Clone();
    BitConverter.GetBytes(invalidCount).CopyTo(invalidHeader, 0);
    Check(ScriptInfo.QueryFromData(invalidHeader) == null, "Reject invalid header without offset overflow");
}
foreach (string message in new[] {
    "「Baris satu\nBaris dua\nBaris tiga\nBaris empat」",
    "『Iya, sedikit. Kalau dijelaskan dengan kata-kata yang bisa dimengerti Yoshiyuki-kun, mungkin semacam penyakit yang nggak bisa disembuhkan.』",
    "「Kakak, pengantin perempuannya, cantik ya」",
    "「Teks ini cukup panjang untuk dibungkus menjadi lebih dari satu baris tanpa kehilangan kata apa pun atau mengubah ukuran huruf.」",
    "「Pertama\r\nKedua\\nKetiga\rKeempat」"
}) {
    string formatted = formatter.Format(message);
    TextFormatter.ValidateBody(formatted, "fixture", TextFormatter.DefaultWrapWidth);
    Check(formatter.Format(formatted) == formatted, "Wrapping must be idempotent");
    Check(formatted.Split('\n').Length <= 4, "Four-line limit");
}
try {
    TextFormatter.ValidateBody("a\nb\nc\nd\ne", "overflow", 46);
    Check(false, "Five lines must be rejected");
} catch (InvalidDataException) { checks++; }

string exported = Path.Combine(output, "template.json");
Check(processor.ExportMesToJson(template, exported) == 0, "Export real MES template");
var entries = Read(exported);
int[] named = entries.Select((entry, index) => (entry, index)).Where(x => x.entry.Name != null).Select(x => x.index).ToArray();
string[] names = ["Yuto", "勇斗", "Yuki", "由姫", "Yuuki", "桜姫", "Yoshiyuki", "義之"];
Check(named.Length >= names.Length, "Template needs eight dialogue entries");
// Keep the real count and name/body structure, isolating these checks from
// unrelated long translations elsewhere in the corpus.
foreach (var entry in entries)
    entry.Message = entry.Name == null ? "Narasi untuk pengujian." : "「Dialog untuk pengujian.」";
for (int i = 0; i < names.Length; i++) {
    entries[named[i]].Name = names[i];
    entries[named[i]].Message = "「Baris satu\nBaris dua\nBaris tiga\nBaris empat」";
}
string input = Path.Combine(output, "names.json");
string firstMes = Path.Combine(output, "first.mes");
string firstJson = Path.Combine(output, "first.json");
Write(input, entries);
Check(processor.ImportJsonToMes(input, template, firstMes) == 0, "Import all distinct portrait names");
Check(processor.ExportMesToJson(firstMes, firstJson) == 0, "Export imported MES");
var roundtrip = Read(firstJson);
Check(roundtrip.Count == entries.Count, "Entry count survives roundtrip");
for (int i = 0; i < entries.Count; i++) {
    Check(roundtrip[i].Name == entries[i].Name, $"Name changed at {i}");
    Check(roundtrip[i].Message == entries[i].Message, $"Text/newline changed at {i}");
}
string secondMes = Path.Combine(output, "second.mes");
Check(processor.ImportJsonToMes(firstJson, firstMes, secondMes) == 0, "Second import");
Check(File.ReadAllBytes(firstMes).SequenceEqual(File.ReadAllBytes(secondMes)), "Repeated conversion must be byte-stable");

var legacy = new List<TextEntry>();
foreach (var entry in entries) {
    if (entry.Name != null) legacy.Add(new TextEntry { Message = entry.Name });
    legacy.Add(new TextEntry { Message = entry.Message });
}
string legacyJson = Path.Combine(output, "legacy.json");
string legacyMes = Path.Combine(output, "legacy.mes");
Write(legacyJson, legacy);
Check(processor.ImportJsonToMes(legacyJson, template, legacyMes) == 0, "Legacy JSON import");
Check(File.ReadAllBytes(firstMes).SequenceEqual(File.ReadAllBytes(legacyMes)), "Legacy and paired JSON differ");

// Fail before touching an existing output when text exceeds the panel limit.
entries[named[0]].Message = "「Satu\nDua\nTiga\nEmpat\nLima」";
string invalid = Path.Combine(output, "overflow.json");
Write(invalid, entries);
byte[] before = File.ReadAllBytes(firstMes);
Check(processor.ImportJsonToMes(invalid, template, firstMes) != 0, "Overflow import must fail");
Check(before.SequenceEqual(File.ReadAllBytes(firstMes)), "Rejected import overwrote output");
Check(logs.Any(line => line.Contains("maximum is 4")), "Actionable overflow diagnostic");
entries.RemoveAt(entries.Count - 1);
Write(invalid, entries);
Check(processor.ImportJsonToMes(invalid, template, firstMes) != 0, "Count mismatch must fail");
Check(before.SequenceEqual(File.ReadAllBytes(firstMes)), "Count mismatch overwrote output");

string report = JsonSerializer.Serialize(new { passed = true, checks, template, distinctNames = names,
    output, repeatedMesByteStable = true, overflowOutputPreserved = true }, new JsonSerializerOptions { WriteIndented = true });
File.WriteAllText(Path.Combine(output, "report.json"), report);
Console.WriteLine(report);
