import sys
import hashlib
import binascii

def analyze_string(label, s):
    print(f"--- {label} ---")
    print(f"String: {s}")
    print(f"Type: {type(s)}")
    try:
        # Get raw bytes if possible or encode
        encoded = s.encode('utf-8')
        print(f"UTF-8 Bytes: {binascii.hexlify(encoded)}")
        md5 = hashlib.md5(encoded).hexdigest()
        print(f"MD5 Hash: {md5}")
    except Exception as e:
        print(f"Error analyzing: {e}")

if __name__ == "__main__":
    # Ensure stdout is utf-8
    sys.stdout.reconfigure(encoding='utf-8')
    
    if len(sys.argv) > 1:
        input_arg = sys.argv[1]
        analyze_string("Argument 1", input_arg)
    else:
        print("No argument provided")
