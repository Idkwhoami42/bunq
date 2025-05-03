import { useState, useEffect } from "react";
import { PieChart, Pie, Cell } from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "~/components/ui/chart";
import type { Pot } from "~/types";

interface SavingsPotTrackerProps {
  pot: Pot;
}

export default function SavingsPotTracker({ pot }: SavingsPotTrackerProps) {
  const [animateProgress, setAnimateProgress] = useState(false);
  const [pieChartData, setPieChartData] = useState<
    Array<{ name: string; value: number; fill: string }>
  >([]);

  // Prepare pie chart data
  useEffect(() => {
    const chartData: Array<{ name: string; value: number; fill: string }> = [];

    // Colors for the pie chart
    const colors = [
      "hsl(var(--chart-1))",
      "hsl(var(--chart-2))",
      "hsl(var(--chart-3))",
      "hsl(var(--chart-4))",
      "hsl(var(--chart-5))",
    ];

    // Add individual savings to chart data
    pot.individual_savings.forEach((saving, index) => {
      const totalContributed = saving.participant_amounts.reduce(
        (sum, participant) => sum + participant.amount_contributed,
        0
      );

      if (totalContributed > 0) {
        chartData.push({
          name: saving.description,
          value: totalContributed,
          fill: colors[index % colors.length],
        });
      }
    });

    // Add shared savings to chart data
    pot.shared_savings.forEach((saving, index) => {
      if (saving.amount_contributed > 0) {
        chartData.push({
          name: saving.description,
          value: saving.amount_contributed,
          fill: colors[(index + pot.individual_savings.length) % colors.length],
        });
      }
    });

    setPieChartData(chartData);
  }, [pot]);

  // Trigger animation after component mounts
  useEffect(() => {
    setAnimateProgress(true);
  }, []);

  // Format currency
  const formatCurrency = (amount: number, currency = "USD") => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
    }).format(amount);
  };

  // Calculate progress percentage
  const calculateProgress = (contributed: number, expected: number) => {
    return Math.min(100, (contributed / expected) * 100);
  };

  // Calculate total contributed and expected amounts
  const totalContributed = [
    ...pot.individual_savings.flatMap((s) => s.participant_amounts),
    ...pot.shared_savings,
  ].reduce(
    (sum, item) =>
      sum + ("amount_contributed" in item ? item.amount_contributed : 0),
    0
  );

  const totalExpected = [
    ...pot.individual_savings.flatMap((s) => s.participant_amounts),
    ...pot.shared_savings,
  ].reduce(
    (sum, item) => sum + ("expected_amount" in item ? item.expected_amount : 0),
    0
  );

  return (
    <div className="w-full max-w-md mx-auto space-y-8">
      {/* Pot description */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <h2 className="text-xl font-semibold text-center text-gray-800">
          {pot.description}
        </h2>
        <p className="text-center text-gray-600 mt-2">
          {formatCurrency(totalContributed)} / {formatCurrency(totalExpected)}
          <span className="text-sm ml-2">
            ({((totalContributed / totalExpected) * 100).toFixed(0)}% complete)
          </span>
        </p>
      </div>

      {/* Pie Chart */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <h3 className="text-lg font-medium text-gray-700 mb-4">
          Savings Distribution
        </h3>
        <div className="h-64">
          {totalContributed > 0 ? (
            <ChartContainer
              config={pieChartData.reduce((config, item) => {
                config[item.name.toLowerCase().replace(/\s+/g, "_")] = {
                  label: item.name,
                  color: item.fill,
                };
                return config;
              }, {} as Record<string, { label: string; color: string }>)}
            >
              <PieChart>
                <ChartTooltip content={<ChartTooltipContent />} />
                <Pie
                  data={pieChartData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  innerRadius={40}
                  paddingAngle={2}
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {pieChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
              </PieChart>
            </ChartContainer>
          ) : (
            <div className="flex flex-col items-center justify-center h-full">
              <ChartContainer
                config={{
                  empty: {
                    label: "No Savings Yet",
                    color: "hsl(var(--muted-foreground))",
                  },
                }}
              >
                <PieChart>
                  <Pie
                    data={[{ name: "No Savings Yet", value: 1 }]}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    innerRadius={40}
                    fill="hsl(var(--muted))"
                  />
                </PieChart>
              </ChartContainer>
              <p className="text-muted-foreground mt-4 text-center">
                No savings contributed yet
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Individual savings section */}
      <div className="space-y-6">
        <h3 className="text-lg font-medium text-gray-700">
          Individual Savings
        </h3>

        {pot.individual_savings.map((saving, index) => (
          <div
            key={`individual-${index}`}
            className="bg-white rounded-lg shadow-md p-4 space-y-4"
          >
            <h4 className="font-medium text-gray-800">{saving.description}</h4>

            <div className="space-y-4">
              {saving.participant_amounts.map((participant, pIndex) => {
                const progressPercentage = calculateProgress(
                  participant.amount_contributed,
                  participant.expected_amount
                );

                return (
                  <div key={`participant-${pIndex}`} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="font-medium">
                        {participant.participant}
                      </span>
                      <span>
                        {formatCurrency(
                          participant.amount_contributed,
                          participant.currency
                        )}{" "}
                        /
                        {formatCurrency(
                          participant.expected_amount,
                          participant.currency
                        )}
                      </span>
                    </div>

                    <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full transition-all duration-1000 ease-out"
                        style={{
                          width: animateProgress
                            ? `${progressPercentage}%`
                            : "0%",
                        }}
                      />
                    </div>

                    <div className="text-xs text-right text-gray-500">
                      {progressPercentage.toFixed(0)}% complete
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Shared savings section */}
      <div className="space-y-6">
        <h3 className="text-lg font-medium text-gray-700">Shared Savings</h3>

        {pot.shared_savings.map((saving, index) => {
          const progressPercentage = calculateProgress(
            saving.amount_contributed,
            saving.expected_amount
          );

          return (
            <div
              key={`shared-${index}`}
              className="bg-white rounded-lg shadow-md p-4 space-y-2"
            >
              <h4 className="font-medium text-gray-800">
                {saving.description}
              </h4>

              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>
                  {formatCurrency(saving.amount_contributed, saving.currency)} /
                  {formatCurrency(saving.expected_amount, saving.currency)}
                </span>
              </div>

              <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full transition-all duration-1000 ease-out"
                  style={{
                    width: animateProgress ? `${progressPercentage}%` : "0%",
                  }}
                />
              </div>

              <div className="text-xs text-right text-gray-500">
                {progressPercentage.toFixed(0)}% complete
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
