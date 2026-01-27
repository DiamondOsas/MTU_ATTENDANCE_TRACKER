import glob
import os

def repair_file(filepath):
    try:
        # We read as utf-8 because the file is ostensibly utf-8, just containing garbage characters
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace mojibake with correct characters
        # âœ— (bytes: C3 A2 C5 93 E2 80 94 in utf-8 view of Windows-1252 of utf-8 bytes... it's complicated, but simple string replacement works)
        # âœ“ (checkmark)
        
        # Note: The user sees "âœ—".
        # If I write a file with "✗" in UTF-8 (E2 9C 97), and read it as Cp1252:
        # E2 -> â
        # 9C -> œ
        # 97 -> —
        # So "âœ—" IS the Cp1252 interpretation of the UTF-8 bytes for "✗".
        
        # If the file was saved AS UTF-8 *while containing these characters*, then the file literally contains:
        # C3 A2 (â) C5 93 (œ) E2 80 94 (—)
        # So we just replace that sequence.
        
        new_content = content.replace("âœ—", "✗").replace("âœ“", "✓")
        
        if content != new_content:
            print(f"Repairing {filepath}...")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
        else:
            print(f"No changes needed for {filepath}")

    except Exception as e:
        print(f"Error repairing {filepath}: {e}")

if __name__ == "__main__":
    for filepath in glob.glob("db/attendance/*.csv"):
        repair_file(filepath)
