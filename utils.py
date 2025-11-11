from collections.abc import Sequence

def format_compression_metrics(
    codecs: Sequence["numcodecs.abc.Codec"],
    *,
    nbytes: "numcodecs_observers.bytesize.BytesizeObserver",
    instructions: "None | numcodecs_wasm.WasmCodecInstructionCounterObserver" = None,
):
    import pandas as pd
    from numcodecs_observers.hash import HashableCodec

    codecs = tuple(codecs)

    encoded_bytes = { c: sum(e.post for e in es) for c, es in nbytes.encode_sizes.items() }
    decoded_bytes = { c: sum(d.post for d in ds) for c, ds in nbytes.decode_sizes.items() }

    table = pd.DataFrame(
        {
            "Codec": [str(c) for c in codecs] + ["Summary"],
            "compression ratio [raw B / enc B]": [
                round(decoded_bytes[HashableCodec(c)] / encoded_bytes[HashableCodec(c)], 2) for c in codecs
            ] + ([
                round(decoded_bytes[HashableCodec(codecs[0])] / encoded_bytes[HashableCodec(codecs[-1])], 2)
            ] if len(codecs) > 0 else [1.0]),
        }
    ).set_index(["Codec"])

    if instructions is not None:
        table["encode instructions [#/B]"] = [
            (round(
                sum(instructions.encode_instructions[HashableCodec(c)])
                / decoded_bytes[HashableCodec(c)],
                1,
            ) if HashableCodec(c) in instructions.encode_instructions else "<unknown>") for c in codecs
        ] + ([
            round(
                sum(sum(instructions.encode_instructions[HashableCodec(c)]) for c in codecs)
                / decoded_bytes[HashableCodec(codecs[0])],
                1,
            ) if all(HashableCodec(c) in instructions.encode_instructions for c in codecs) else "<unknown>"
        ] if len(codecs) > 0 else [0.0])

        table["decode instructions [#/B]"] = [
            (round(
                sum(instructions.decode_instructions[HashableCodec(c)])
                / decoded_bytes[HashableCodec(c)],
                1,
            ) if HashableCodec(c) in instructions.decode_instructions else "<unknown>") for c in codecs
        ] + ([
            round(
                sum(sum(instructions.decode_instructions[HashableCodec(c)]) for c in codecs)
                / decoded_bytes[HashableCodec(codecs[0])],
                1,
            ) if all(HashableCodec(c) in instructions.decode_instructions for c in codecs) else "<unknown>"
        ] if len(codecs) > 0 else [0.0])

    return table
