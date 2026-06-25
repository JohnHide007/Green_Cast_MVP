"use client";

/**
 * RiskGauge — 270° SVG donut speedometer
 *
 * Score 0-100 rendered as an arc fill.
 *   < 34  → green  (#2E7D32)
 *  34-67  → amber  (#D97706)
 *   > 67  → red    (#B91C1C)
 *
 * Props:
 *   score  — 0-100
 *   size   — "sm" | "md" | "lg"  (80 / 120 / 160 px)
 *   label  — optional text below the number (defaults to risk tier)
 */

interface RiskGaugeProps {
  score: number;
  size?: "sm" | "md" | "lg";
  label?: string;
}

const SIZE_MAP = {
  sm: 80,
  md: 120,
  lg: 160,
} as const;

function trackColour(score: number): string {
  if (score < 34) return "#2E7D32";
  if (score < 67) return "#D97706";
  return "#B91C1C";
}

function riskTier(score: number): string {
  if (score < 34) return "Low Risk";
  if (score < 67) return "Moderate";
  return "High Risk";
}

/**
 * Describe an SVG arc path for a donut gauge.
 *
 * The gauge runs 270° starting at 135° (bottom-left) and sweeping clockwise
 * to 45° (bottom-right), so the gap is at the bottom.
 */
function arcPath(cx: number, cy: number, r: number, pct: number): string {
  const startDeg = 135;
  const totalDeg = 270;
  const sweepDeg = Math.min(pct * totalDeg, 269.99);

  const toRad = (d: number) => (d * Math.PI) / 180;

  const x1 = cx + r * Math.cos(toRad(startDeg));
  const y1 = cy + r * Math.sin(toRad(startDeg));

  const endDeg = startDeg + sweepDeg;
  const x2 = cx + r * Math.cos(toRad(endDeg));
  const y2 = cy + r * Math.sin(toRad(endDeg));

  const largeArc = sweepDeg > 180 ? 1 : 0;

  return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`;
}

export function RiskGauge({ score, size = "md", label }: RiskGaugeProps) {
  const px = SIZE_MAP[size];
  const cx = px / 2;
  const cy = px / 2;

  const strokeW = size === "sm" ? 6 : size === "md" ? 9 : 12;
  const r = (px - strokeW * 2) / 2 - 2;

  const pct = Math.max(0, Math.min(score, 100)) / 100;
  const colour = trackColour(score);
  const tier = label ?? riskTier(score);

  const scoreFontSize = size === "sm" ? 18 : size === "md" ? 26 : 36;
  const labelFontSize = size === "sm" ? 7 : size === "md" ? 9 : 11;
  const labelY = size === "sm" ? cy + 9 : size === "md" ? cy + 13 : cy + 18;

  const trackPath = arcPath(cx, cy, r, 1);
  const fillPath = arcPath(cx, cy, r, pct);

  return (
    <svg
      width={px}
      height={px}
      viewBox={`0 0 ${px} ${px}`}
      aria-label={`Risk gauge: ${score.toFixed(1)} — ${tier}`}
      role="img"
    >
      {/* Background track */}
      <path
        d={trackPath}
        fill="none"
        stroke="#E5E7EB"
        strokeWidth={strokeW}
        strokeLinecap="round"
      />

      {/* Coloured fill arc */}
      {pct > 0 && (
        <path
          d={fillPath}
          fill="none"
          stroke={colour}
          strokeWidth={strokeW}
          strokeLinecap="round"
        />
      )}

      {/* Score number */}
      <text
        x={cx}
        y={cy + scoreFontSize * 0.35}
        textAnchor="middle"
        fontSize={scoreFontSize}
        fontFamily="'JetBrains Mono', Menlo, monospace"
        fontWeight="700"
        fill={colour}
      >
        {score.toFixed(0)}
      </text>

      {/* Label */}
      <text
        x={cx}
        y={labelY + scoreFontSize * 0.35}
        textAnchor="middle"
        fontSize={labelFontSize}
        fontFamily="Inter, system-ui, sans-serif"
        fontWeight="500"
        fill="#6B7280"
        letterSpacing="0.04em"
      >
        {tier.toUpperCase()}
      </text>
    </svg>
  );
}
