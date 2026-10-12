namespace DC2DMMesTextTool;

/// <summary>
/// Script configuration for Da Capo 2 Dearest Marriage.
/// Based on MesTextTool's script_info.cpp
/// </summary>
public class ScriptInfo
{
    public string Name { get; init; } = "";
    public ushort Version { get; init; }
    public OffsetType OffsetType { get; init; }
    
    // Opcode ranges for different instruction types
    public (byte Begin, byte End) Uint8x2 { get; init; }   // [op][arg1:byte][arg2:byte]
    public (byte Begin, byte End) Uint8Str { get; init; }  // [op][arg1:byte][string]
    public (byte Begin, byte End) String { get; init; }    // [op][string] - unencrypted
    public (byte Begin, byte End) EncStr { get; init; }    // [op][encstring] - encrypted
    public (byte Begin, byte End) Uint16x4 { get; init; }  // [op][4 x uint16]
    
    public byte EncryptionKey { get; init; }
    public byte[] OutputOpcodes { get; init; } = Array.Empty<byte>();
    
    /// <summary>
    /// Check if an opcode falls within a section range
    /// </summary>
    public bool IsInSection((byte Begin, byte End) section, byte opcode)
    {
        if (section.Begin == 0xFF && section.End == 0xFF)
            return false;
        return opcode >= section.Begin && opcode <= section.End;
    }
    
    /// <summary>
    /// D.C.II Dearest Marriage configuration
    /// Note: DC2DM uses Offset2 (labelCount * 6 + 4) per original C++ MesTextTool
    /// </summary>
    public static readonly ScriptInfo DC2DM = new()
    {
        Name = "dc2dm",
        Version = 0x9D72,
        OffsetType = OffsetType.Offset2,
        Uint8x2 = (0x00, 0x29),
        Uint8Str = (0x2A, 0x31),
        String = (0x32, 0x4C),
        EncStr = (0x4D, 0x50),
        Uint16x4 = (0x51, 0xFF),
        EncryptionKey = 0x20,
        OutputOpcodes = new byte[] { 0x44 }
    };

    /// <summary>Supported configuration: Da Capo 2 Dearest Marriage.</summary>
    public static readonly ScriptInfo[] AllInfos = { DC2DM };

    /// <summary>
    /// Query script info by name
    /// </summary>
    public static ScriptInfo? QueryByName(string name)
    {
        return AllInfos.FirstOrDefault(i => 
            i.Name.Equals(name, StringComparison.OrdinalIgnoreCase));
    }
    
    /// <summary>
    /// Query script info from MES file data
    /// </summary>
    public static ScriptInfo? QueryFromData(byte[] data)
    {
        if (data.Length < 8)
            return null;
            
        int labelCount = BitConverter.ToInt32(data, 0);
        long offset = (long)labelCount * 6 + 4;
        if (labelCount < 1 || offset + 3 > data.Length ||
            BitConverter.ToInt32(data, 4) != 3)
            return null;

        return BitConverter.ToUInt16(data, (int)offset) == DC2DM.Version
            ? DC2DM : null;
    }
}

public enum OffsetType
{
    Offset1,  // head[0] * 4 + 4
    Offset2   // head[0] * 6 + 4
}
