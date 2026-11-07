import React, { useState } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import { CompetitorProfile } from "../types";

interface ScorecardViewProps {
  profiles: CompetitorProfile[];
}

const ENTITY_COLORS = [
  "#6366F1", // Indigo (Primary)
  "#14B8A6", // Teal
  "#F59E0B", // Amber
  "#EC4899", // Pink
  "#8B5CF6", // Violet
  "#3B82F6", // Blue
];

export const ScorecardView: React.FC<ScorecardViewProps> = ({ profiles }) => {
  if (!profiles || profiles.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        No scored profiles available.
      </div>
    );
  }

  // Extract all unique aspects
  const allAspects: string[] = [];
  profiles.forEach((p) => {
    Object.keys(p.aspect_scores || {}).forEach((asp) => {
      if (!allAspects.includes(asp)) {
        allAspects.push(asp);
      }
    });
  });

  // State to toggle entity visibility in the radar chart
  const [visibleEntities, setVisibleEntities] = useState<Record<string, boolean>>(() => {
    const init: Record<string, boolean> = {};
    profiles.forEach((p, idx) => {
      init[p.entity] = idx < 3; // Enable first 3 by default
    });
    return init;
  });

  const toggleEntity = (entity: string) => {
    setVisibleEntities((prev) => ({ ...prev, [entity]: !prev[entity] }));
  };

  // Build Radar data format: [{ aspect: "product", EntityA: 4, EntityB: 3, ... }]
  const radarData = allAspects.map((aspect) => {
    const item: any = { aspect };
    profiles.forEach((p) => {
      item[p.entity] = p.aspect_scores?.[aspect] || 1;
    });
    return item;
  });

  // Build Ranked Average Bar data: [{ entity: "CoinDCX", score: 4.8 }, ...]
  const rankedData = profiles
    .map((p) => {
      const scores = Object.values(p.aspect_scores || {});
      const avg = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 1;
      return {
        entity: p.entity,
        average: parseFloat(avg.toFixed(2)),
      };
    })
    .sort((a, b) => b.average - a.average);

  return (
    <div className="flex flex-col gap-6 h-full overflow-y-auto pr-1">
      {/* Radar Chart Card */}
      <div className="bg-dark-surface dark:bg-[#12151C] light:bg-white rounded-2xl border border-dark-border dark:border-white/10 light:border-black/10 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
          <div>
            <h3 className="text-base font-semibold text-gray-100 dark:text-gray-100 light:text-gray-900">
              Multi-Dimensional Competitor Radar
            </h3>
            <p className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-500 mt-0.5">
              1-5 strategic scoring per evaluated aspect.
            </p>
          </div>

          {/* Legend toggle pills */}
          <div className="flex flex-wrap gap-2">
            {profiles.map((p, idx) => {
              const active = visibleEntities[p.entity];
              const color = ENTITY_COLORS[idx % ENTITY_COLORS.length];
              return (
                <button
                  key={p.entity}
                  type="button"
                  onClick={() => toggleEntity(p.entity)}
                  className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs rounded-lg font-medium border transition-all cursor-pointer ${
                    active
                      ? "bg-white/10 dark:bg-white/10 light:bg-gray-100 border-white/20 text-gray-200 dark:text-gray-200 light:text-gray-800"
                      : "bg-transparent border-white/5 text-gray-500 opacity-50"
                  }`}
                >
                  <span
                    className="w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span>{p.entity}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="w-full h-80">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255, 255, 255, 0.1)" />
              <PolarAngleAxis
                dataKey="aspect"
                tick={{ fill: "#9CA3AF", fontSize: 11 }}
              />
              <PolarRadiusAxis
                angle={30}
                domain={[0, 5]}
                stroke="rgba(255, 255, 255, 0.2)"
                tick={{ fill: "#6B7280", fontSize: 10 }}
              />
              {profiles.map((p, idx) => {
                if (!visibleEntities[p.entity]) return null;
                const color = ENTITY_COLORS[idx % ENTITY_COLORS.length];
                return (
                  <Radar
                    key={p.entity}
                    name={p.entity}
                    dataKey={p.entity}
                    stroke={color}
                    fill={color}
                    fillOpacity={0.25}
                  />
                );
              })}
              <Tooltip
                contentStyle={{
                  backgroundColor: "#181C25",
                  borderColor: "rgba(255,255,255,0.1)",
                  borderRadius: "12px",
                  fontSize: "12px",
                  color: "#fff",
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Ranked Overall Bar Chart */}
      <div className="bg-dark-surface dark:bg-[#12151C] light:bg-white rounded-2xl border border-dark-border dark:border-white/10 light:border-black/10 p-6 shadow-sm">
        <h3 className="text-base font-semibold text-gray-100 dark:text-gray-100 light:text-gray-900 mb-1">
          Ranked Strategic Benchmark
        </h3>
        <p className="text-xs text-gray-400 dark:text-gray-400 light:text-gray-500 mb-4">
          Composite score across all analyzed dimensions (maximum 5.0).
        </p>

        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={rankedData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
            >
              <XAxis type="number" domain={[0, 5]} tick={{ fill: "#9CA3AF", fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="entity"
                tick={{ fill: "#9CA3AF", fontSize: 12 }}
                width={90}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#181C25",
                  borderColor: "rgba(255,255,255,0.1)",
                  borderRadius: "12px",
                  fontSize: "12px",
                  color: "#fff",
                }}
              />
              <Bar dataKey="average" radius={[0, 8, 8, 0]}>
                {rankedData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={ENTITY_COLORS[index % ENTITY_COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
