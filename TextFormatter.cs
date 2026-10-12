using System.Text;
using System.Text.RegularExpressions;

namespace DC2DMMesTextTool;

/// <summary>Word wrapping in native 11px half-width cells, never font scaling.</summary>
public class TextFormatter
{
    // Backlog body starts at x=364 and ends before x=880: 46 * 11 = 506px.
    public const int DefaultWrapWidth = 46;
    public const int MaxBodyLines = 4;
    public int MinLineLength { get; set; } = 18; // Retained for API compatibility.
    public int MaxLineLength { get; set; } = DefaultWrapWidth;

    private static readonly Regex Tokens = new(
        @"@[A-Za-z][0-9]*|｛[^｝]*｝|[ \t]+|[\x21-\x7e-[\x40]]+|.", RegexOptions.Compiled);
    private const string Closing = "。、？！’”，！～】；：）」』…,.!?;:";
    private const string Opening = "（(「『【‘“";

    public static string NormalizeNewlines(string text) =>
        text.Replace("\r\n", "\n").Replace('\r', '\n').Replace("\\n", "\n");

    private static IEnumerable<string> WrapTokens(string paragraph)
    {
        var tokens = new List<string>();
        foreach (Match match in Tokens.Matches(paragraph))
        {
            string token = match.Value;
            if (token.Length == 1 && Closing.Contains(token[0]) && tokens.Count > 0 &&
                !string.IsNullOrWhiteSpace(tokens[^1]) && !tokens[^1].StartsWith('@'))
                tokens[^1] += token;
            else
                tokens.Add(token);
        }
        return tokens;
    }

    public string Format(string text)
    {
        if (string.IsNullOrEmpty(text)) return text;
        if (MaxLineLength < 1) throw new ArgumentOutOfRangeException(nameof(MaxLineLength));
        var output = new List<string>();
        int fontSize = 22;
        // Preserve intentional line boundaries and make repeated conversions stable.
        foreach (string paragraph in NormalizeNewlines(text).Split('\n'))
        {
            var line = new StringBuilder();
            double width = 0;
            string pendingSpace = "";
            foreach (string token in WrapTokens(paragraph))
            {
                if (token[0] == '@' && token.Length >= 2 && char.IsLetter(token[1]))
                {
                    line.Append(token);
                    fontSize = token switch { "@s" => 16, "@m" => 22, "@l" => 32, "@r" => 12, "@u" => 9, _ => fontSize };
                    continue;
                }
                if (token.All(c => c == ' ' || c == '\t'))
                {
                    pendingSpace += token.Replace("\t", " ");
                    continue;
                }
                double CellWidth(char c) => (c <= 0x7f ? fontSize / 2 : fontSize) / 11.0;
                double tokenWidth = token.Sum(CellWidth);
                double gapWidth = pendingSpace.Length * (fontSize / 2) / 11.0;
                if (width > 0 && width + gapWidth + tokenWidth > MaxLineLength)
                {
                    if (!(token.Length == 1 && Closing.Contains(token[0])))
                    {
                        string completed = line.ToString();
                        string carry = "";
                        if (completed.Length > 0 && Opening.Contains(completed[^1]))
                        {
                            carry = completed[^1].ToString();
                            completed = completed[..^1];
                        }
                        output.Add(completed.TrimEnd());
                        line.Clear();
                        line.Append(carry);
                        width = carry.Sum(CellWidth);
                        pendingSpace = "";
                        gapWidth = 0;
                    }
                }
                line.Append(pendingSpace);
                line.Append(token);
                width += gapWidth + tokenWidth;
                pendingSpace = "";
            }
            line.Append(pendingSpace);
            output.Add(line.ToString().TrimEnd());
        }
        return string.Join("\n", output);
    }

    public static void ValidateBody(string text, string location, int widthLimit)
    {
        string[] lines = text.Split('\n');
        if (lines.Length > MaxBodyLines)
            throw new InvalidDataException($"{location}: {lines.Length} lines after wrapping; maximum is {MaxBodyLines}. Shorten/reword this message or adjust its explicit newlines. No text was truncated and no MES was written.");
        int fontSize = 22;
        for (int i = 0; i < lines.Length; i++)
        {
            double width = 0;
            foreach (Match match in Tokens.Matches(lines[i]))
            {
                string token = match.Value;
                if (token[0] == '@' && token.Length >= 2 && char.IsLetter(token[1]))
                {
                    fontSize = token switch { "@s" => 16, "@m" => 22, "@l" => 32, "@r" => 12, "@u" => 9, _ => fontSize };
                    continue;
                }
                width += token.Sum(c => (c <= 0x7f ? fontSize / 2 : fontSize) / 11.0);
            }
            if (width > widthLimit + 0.001)
                throw new InvalidDataException($"{location}, line {i + 1}: exceeds width {widthLimit}. Reword the long word or adjust the line break. No text was truncated and no MES was written.");
        }
    }
}
