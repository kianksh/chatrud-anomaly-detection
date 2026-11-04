import argparse
from pathlib import Path

from chatrud_anomaly import load_geochemical_data, run_pipeline
from chatrud_anomaly.plotting import apply_style
from chatrud_anomaly.reporting import save_figures, write_excel_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Detect geochemical anomalies with Isolation Forest and percentile filters."
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to the lab Excel workbook.")
    parser.add_argument("--sheet", default="Sheet2", help="Worksheet name (default: Sheet2).")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--contamination", type=float, default=0.10)
    parser.add_argument("--n-estimators", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-plots", action="store_true", help="Skip figure and map export.")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.input.is_file():
        raise SystemExit(f"Input file not found: {args.input}")

    data = load_geochemical_data(args.input, sheet_name=args.sheet)
    result = run_pipeline(
        data,
        contamination=args.contamination,
        n_estimators=args.n_estimators,
        random_state=args.seed,
    )

    report_path = write_excel_report(result, args.output_dir / "anomalies_report.xlsx")
    print(result.summary().to_string())
    print(f"Report written to {report_path}")

    if not args.no_plots:
        apply_style()
        save_figures(result, args.output_dir / "figures")
        print(f"Figures written to {args.output_dir / 'figures'}")


if __name__ == "__main__":
    main()
