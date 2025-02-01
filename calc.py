from config import *
from pathlib import Path
import polars as pl
from polars import col as c
import polars.selectors as cs

def get_files() -> list[str]:
    return [str(file.stem) for file in DATA_DIR.iterdir()]

def is_special() -> pl.Expr:
    return c.product.is_in(pl.read_parquet('specialty/specialty_list.parquet').select(c.product).to_series()).alias('is_special')

def dos():
    return pl.date(c.year,c.month,15).dt.month_start().alias('dos')

def load_ftc_list():
    return pl.scan_parquet('specialty/ftc_product.parquet').collect().to_series()

def is_ftc():
    return c.product.is_in(load_ftc_list()).alias('is_ftc')

def load_files(files: list[str]|None) -> pl.LazyFrame:
    if files:
        return pl.scan_parquet([DATA_DIR / f'{file}.parquet' for file in files]).with_columns(c.drug_class.replace(GROUP_DICT),is_special(),dos(),is_ftc())
    return pl.scan_parquet(DATA_DIR / '*.parquet').with_columns(c.drug_class.replace(GROUP_DICT),is_special(),dos(),is_ftc())

def mc_diff():
    return (c.total - c.mc_total).alias('mc_diff')

def mc_diff_per_rx():
    return (mc_diff() / c.rx_ct).alias('per_rx')

def dict_for_kpis(data: pl.LazyFrame) -> dict:
    return (
    data
    .select(cs.contains('total', 'rx_ct').sum())
    .with_columns(mc_diff())
    .with_columns(mc_diff_per_rx())
    .collect()
    .rename({})
    .to_dict(as_series=False)
    )
