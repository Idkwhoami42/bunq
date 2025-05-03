"use client"

import { useEffect, useState } from "react"
import { ArrowUp, ArrowDown, Trophy, DollarSign } from "lucide-react"
import type { Pot } from "~/types"

export type LeaderboardEntry = {
    participant: string
    totalExpected: number
    totalContributed: number
    completionPercentage: number
  }

interface LeaderboardSectionProps {
  pot: Pot
}

export default function LeaderboardSection({ pot }: LeaderboardSectionProps) {
  const [animateProgress, setAnimateProgress] = useState(false)
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([])

  // Calculate leaderboard data
  useEffect(() => {
    const participantTotals: Record<string, { expected: number; contributed: number }> = {}

    // Collect data from all individual savings
    pot.individual_savings.forEach((saving) => {
      saving.participant_amounts.forEach((participant) => {
        if (!participantTotals[participant.participant]) {
          participantTotals[participant.participant] = { expected: 0, contributed: 0 }
        }
        participantTotals[participant.participant].expected += participant.expected_amount
        participantTotals[participant.participant].contributed += participant.amount_contributed
      })
    })

    // Convert to leaderboard entries and sort
    const leaderboardData = Object.entries(participantTotals).map(([participant, totals]) => ({
      participant,
      totalExpected: totals.expected,
      totalContributed: totals.contributed,
      completionPercentage: (totals.contributed / totals.expected) * 100,
    }))

    // Sort by completion percentage (highest first)
    leaderboardData.sort((a, b) => b.completionPercentage - a.completionPercentage)

    setLeaderboard(leaderboardData)
  }, [pot])

  // Trigger animation after component mounts
  useEffect(() => {
    setAnimateProgress(true)
  }, [])

  // Format currency
  const formatCurrency = (amount: number, currency = "USD") => {
    return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-4 space-y-4">
      <h3 className="text-lg font-medium text-gray-700 flex items-center">
        <Trophy className="w-5 h-5 mr-2 text-yellow-500" />
        Leaderboard
      </h3>

      <div className="space-y-4">
        {leaderboard.map((entry, index) => {
          const progressPercentage = entry.completionPercentage
          const medalColor =
            index === 0
              ? "text-yellow-500"
              : index === 1
                ? "text-gray-400"
                : index === 2
                  ? "text-amber-700"
                  : "text-gray-600"

          return (
            <div key={`leaderboard-${index}`} className="relative">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center">
                  <span className={`font-bold mr-2 ${medalColor}`}>{index + 1}</span>
                  <span className="font-medium">{entry.participant}</span>
                </div>
                <div className="text-sm">
                  <DollarSign className="w-4 h-4 inline-block" />
                  {formatCurrency(entry.totalContributed)}
                </div>
              </div>

              <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ease-out ${
                    index === 0
                      ? "bg-yellow-500"
                      : index === 1
                        ? "bg-gray-400"
                        : index === 2
                          ? "bg-amber-700"
                          : "bg-gray-600"
                  }`}
                  style={{
                    width: animateProgress ? `${progressPercentage}%` : "0%",
                  }}
                />
              </div>

              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span className="flex items-center">
                  {progressPercentage >= 100 ? (
                    <ArrowUp className="w-3 h-3 text-green-500 mr-1" />
                  ) : (
                    <ArrowDown className="w-3 h-3 text-red-500 mr-1" />
                  )}
                  {progressPercentage.toFixed(0)}%
                </span>
                <span>
                  {formatCurrency(entry.totalContributed)} /{formatCurrency(entry.totalExpected)}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
