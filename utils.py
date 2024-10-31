import pandas as _pd


def format_compress_stats(
    codecs: list["numcodecs.abc.Codec"],
    stats: list["fcbench.compressor.types.CodecPerformanceMeasurement"],
):
    table = _pd.DataFrame(
        {
            "Codec": [],
            "compression ratio [raw B / enc B]": [],
            "encode instructions [#/B]": [],
            "decode instructions [#/B]": [],
        }
    ).set_index(["Codec"])

    for codec, stat in zip(codecs, stats):
        table.loc[str(codec), :] = [
            round(stat.decoded_bytes / stat.encoded_bytes, 2),
            round(stat.encode_instructions / stat.decoded_bytes, 1)
            if stat.encode_instructions is not None
            else None,
            round(stat.decode_instructions / stat.decoded_bytes, 1)
            if stat.decode_instructions is not None
            else None,
        ]

    return table
