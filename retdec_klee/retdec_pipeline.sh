set -e

INPUT="$(pwd)/input"
OUTPUT="$(pwd)/output"

dd if=../Firmware/walk400h.bin of="$INPUT"/fw_256k.bin bs=1 count=$((0x40000))
chmod 777 "$INPUT"/fw_256k.bin

retdec-decompiler \
  -a thumb -e little -m raw \
  --raw-entry-point 0x08001e34 \
  --raw-section-vma 0x08000000 \
  --no-memory-limit \
  "$INPUT"/fw_256k.bin

