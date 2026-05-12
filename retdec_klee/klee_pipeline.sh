#!/bin/bash
set -e

INPUT="$(pwd)/input"
OUTPUT="$(pwd)/output"
WRAPPERS="$(pwd)/wrappers"

echo "[1] Pulizia IR..."
grep -v 'uselistorder' "$INPUT"/fw_256k.bin.ll > "$INPUT"/fw_step1.ll

# Fix variabile globale senza nome
sed -i 's/@0 = external global i32/@0 = global i32 0/' "$INPUT"/fw_step1.ll

# Fix globali malformate
sed -i 's/@global_var_800bd18 = local_unnamed_addr constant \[4 x i16\] %wide-string/@global_var_800bd18 = local_unnamed_addr constant [4 x i16] zeroinitializer/g' "$INPUT"/fw_step1.ll
sed -i 's/@global_var_800bd1a = local_unnamed_addr constant \[3 x i16\] %wide-string/@global_var_800bd1a = local_unnamed_addr constant [3 x i16] zeroinitializer/g' "$INPUT"/fw_step1.ll

# Rinomina funzioni con punti
sed -i 's/@__asm_sxth\.w/@__asm_sxth_w/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vhsub\.u8/@__asm_vhsub_u8/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vmlal\.u32/@__asm_vmlal_u32/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vst1\.8/@__asm_vst1_8/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vst4\.8/@__asm_vst4_8/g' "$INPUT"/fw_step1.ll

# Rinomina funzioni con punti nel nome (non validi in C)
sed -i 's/@__asm_ldc2\.8/@__asm_ldc2_8/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldc2l\.24/@__asm_ldc2l_24/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldclgt\.4/@__asm_ldclgt_4/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldcllo\.32/@__asm_ldcllo_32/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldcllt\.5/@__asm_ldcllt_5/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldclmi\.22/@__asm_ldclmi_22/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldclt\.23/@__asm_ldclt_23/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldclvs\.33/@__asm_ldclvs_33/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldcmi\.25/@__asm_ldcmi_25/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_ldcvs\.1/@__asm_ldcvs_1/g' "$INPUT"/fw_step1.ll

# ARM Coprocessor Store instructions
sed -i 's/@__asm_stc2\.12/@__asm_stc2_12/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_stc2l\.2/@__asm_stc2l_2/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_stceq\.6/@__asm_stceq_6/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_stclhs\.30/@__asm_stclhs_30/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_stcllo\.3/@__asm_stcllo_3/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_stclmi\.26/@__asm_stclmi_26/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_stclne\.31/@__asm_stclne_31/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_stcvs\.27/@__asm_stcvs_27/g' "$INPUT"/fw_step1.ll

# NEON/SIMD instructions
sed -i 's/@__asm_vaddl\.u8/@__asm_vaddl_u8/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vcge\.f32/@__asm_vcge_f32/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vcgt\.s8/@__asm_vcgt_s8/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vcgt\.u32/@__asm_vcgt_u32/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vhadd\.s8/@__asm_vhadd_s8/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vhadd\.u8/@__asm_vhadd_u8/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vhadd\.u8\.35/@__asm_vhadd_u8_35/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vldrle\.16/@__asm_vldrle_16/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vmov\.21/@__asm_vmov_21/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vnmulvs\.f16/@__asm_vnmulvs_f16/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vpmax\.f32/@__asm_vpmax_f32/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vpmin\.f32/@__asm_vpmin_f32/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vrsra\.u32/@__asm_vrsra_u32/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vshl\.u32/@__asm_vshl_u32/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vst2\.8/@__asm_vst2_8/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vst4\.32\.20/@__asm_vst4_32_20/g' "$INPUT"/fw_step1.ll
sed -i 's/@__asm_vhadd_u8\.35/@__asm_vhadd_u8_35/g' "$INPUT"/fw_step1.ll

# Rimuovi vecchi target
sed -i '/^target datalayout = "e-p:32:32/d' "$INPUT"/fw_step1.ll
sed -i '/^target triple = "thumb/d' "$INPUT"/fw_step1.ll

###################################################################################################################

echo "[2] Cambio target triple a x86_64..."
# Sostituisci ALL'INIZIO del file
sed -i '1s/^/target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"\ntarget triple = "x86_64-unknown-linux-gnu"\n\n/' "$INPUT"/fw_step1.ll

###################################################################################################################

echo "[3] Patching LLVM IR per aggiungere var. globale @klee_magic_buffer"
sed -i '/^  %stack_var_-40 = alloca i32, align 4$/d' "$INPUT"/fw_step1.ll

echo "  [3.1] Aggiungendo @klee_magic_buffer..."
sed -i '/^source_filename.*/a \\n@klee_magic_buffer = global [32 x i8] zeroinitializer, align 4' "$INPUT/fw_step1.ll"

echo "  [3.2] Sostituendo riferimenti %stack_var_-40 → @klee_magic_buffer..."
sed -i 's/%stack_var_-40/@klee_magic_buffer/g' "$INPUT/fw_step1.ll"

# STEP 4: Rimuovi eventuali alloca invalide create per errore
echo "  [3.3] Pulizia alloca invalide..."
sed -i '/@klee_magic_buffer = alloca/d' "$INPUT/fw_step1.ll"

###################################################################################################################

echo "[4] Pulizia load e store MMIO"

python3 << EOF
import re

with open("$INPUT/fw_step1.ll", "r") as f:
    lines = f.readlines()

with open("$INPUT/fw_step1.ll", "w") as f:
    for line in lines:
        # Sostituisci load da inttoptr con add 0, 0
        if re.search(r'\s*=\s*load.*inttoptr.*', line):
            p = line.split(", ")
            typ = p[0].split(" = ")[1].split(" ")[1]
            f.write(p[0].split(" = ")[0] + " = " + "add " + typ + " 0, 0\n")
        # Commenta tutte le istruzioni store
        elif line.strip().startswith("store "):
            f.write("; " + line)
        else:
            f.write(line)
EOF

###################################################################################################################

echo "[5] Tutte le funzioni messe a WEAK"
sed -i 's/^define \(.*\) @/define weak \1 @/g' "$INPUT"/fw_step1.ll

###################################################################################################################

echo "[6] Assemblaggio FW..."
llvm-as "$INPUT"/fw_step1.ll -o "$OUTPUT"/fw_raw.bc

###################################################################################################################

echo "[7] Ottimizzazione FW (risolve duplicati)..."
opt -p 'mem2reg,instnamer,simplifycfg' "$OUTPUT"/fw_raw.bc -o "$OUTPUT"/fw_256k_fixed.bc

###################################################################################################################

echo "[8] Compilazione wrapper e stub (stesso target)..."
clang -DKLEE -emit-llvm -c -O0 -g "$WRAPPERS"/wrapper.c -o "$OUTPUT"/wrapper.bc

clang -DKLEE -emit-llvm -c -O0 -g "$WRAPPERS"/arm_stubs.c -o "$OUTPUT"/arm_stubs.bc

clang -DKLEE -emit-llvm -c -O0 -g "$WRAPPERS"/klee_target_stubs.c -o "$OUTPUT"/klee_target_stubs.bc

clang -DKLEE -emit-llvm -c -O0 -g "$WRAPPERS"/unknown_stubs.c -o "$OUTPUT"/unknown_stubs.bc

echo "  [8.1] Merging stubs..."
llvm-link \
  "$OUTPUT"/klee_target_stubs.bc \
  "$OUTPUT"/arm_stubs.bc \
  "$OUTPUT"/unknown_stubs.bc \
  "$OUTPUT"/wrapper.bc \
  -o "$OUTPUT"/all_stubs.bc

###################################################################################################################

echo "[9] Linking..."
llvm-link \
  --override="$OUTPUT"/wrapper.bc \
  "$OUTPUT"/all_stubs.bc \
  "$OUTPUT"/fw_256k_fixed.bc \
  -o "$OUTPUT"/boot_final.bc

# Disassembla per debug
llvm-dis "$OUTPUT"/boot_final.bc -o "$OUTPUT"/boot_final.ll

###################################################################################################################

echo "[10] Esecuzione KLEE..."
klee \
  --external-calls=all \
  --max-memory=8192 \
  --max-time=300 \
  --search=dfs \
  --write-paths \
  "$OUTPUT"/boot_final.bc

klee-stats "$OUTPUT"/klee-last

ktest-tool "$OUTPUT"/klee-last/test000001.ktest

echo "✓ Completato!"