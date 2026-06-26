import { RoiCalculator } from "@/components/roi-calculator";

export default function RoiPage() {
  return (
    <div className="mx-auto max-w-screen-xl px-6 py-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight text-gc-text">ROI Calculator</h1>
        <p className="mt-1 text-sm text-gc-muted">
          Quantify the analyst hours Green Cast replaces versus the platform cost.
        </p>
      </div>
      <RoiCalculator />
    </div>
  );
}
