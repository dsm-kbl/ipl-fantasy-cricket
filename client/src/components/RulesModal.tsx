import { useEffect, useState } from "react";

export default function RulesModal() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const seen = localStorage.getItem("rules_seen");
    if (!seen) {
      setOpen(true);
      localStorage.setItem("rules_seen", "1");
    }
  }, []);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-2xl px-6 py-4 text-white">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-extrabold flex items-center gap-2">🏏 How to Play</h2>
            <button onClick={() => setOpen(false)} className="text-white/70 hover:text-white text-xl">✕</button>
          </div>
        </div>
        <div className="px-6 py-5 space-y-4 text-sm text-gray-700">

          <div>
            <h3 className="font-bold text-gray-900 mb-1">📋 Build Your Team</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Pick exactly <span className="font-semibold">11 players</span> from the two teams playing</li>
              <li>Stay within the <span className="font-semibold">100 credit budget</span></li>
              <li>Maximum <span className="font-semibold">4 overseas players</span> (marked with ✈️)</li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-gray-900 mb-1">👥 Team Composition</h3>
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-gray-50 rounded-lg px-3 py-2 text-center">
                <p className="font-bold text-gray-900">1+</p>
                <p className="text-xs text-gray-500">Wicket-keeper</p>
              </div>
              <div className="bg-gray-50 rounded-lg px-3 py-2 text-center">
                <p className="font-bold text-gray-900">4+</p>
                <p className="text-xs text-gray-500">Batsmen</p>
              </div>
              <div className="bg-gray-50 rounded-lg px-3 py-2 text-center">
                <p className="font-bold text-gray-900">3+</p>
                <p className="text-xs text-gray-500">Bowlers</p>
              </div>
              <div className="bg-gray-50 rounded-lg px-3 py-2 text-center">
                <p className="font-bold text-gray-900">1+</p>
                <p className="text-xs text-gray-500">All-rounder</p>
              </div>
            </div>
          </div>

          <div>
            <h3 className="font-bold text-gray-900 mb-1">🔒 Lockout</h3>
            <p className="text-gray-600">Team selection locks <span className="font-semibold">1 hour before</span> the match starts. Make sure to finalize your team before then.</p>
          </div>

          <div>
            <h3 className="font-bold text-gray-900 mb-1">🎯 Bonus Predictions</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Predict the <span className="font-semibold">toss winner</span> → +10 bonus points</li>
              <li>Predict the <span className="font-semibold">Man of the Match</span> → +25 bonus points</li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-gray-900 mb-1">📊 Scoring</h3>
            <p className="text-gray-600">Points are awarded based on real match performance — runs, wickets, catches, and more. Your team score is the sum of your 11 players' points plus any prediction bonuses.</p>
          </div>

          <div>
            <h3 className="font-bold text-gray-900 mb-1">🏆 Leaderboard</h3>
            <p className="text-gray-600">Compete with other players! The overall leaderboard ranks by cumulative points across all matches.</p>
          </div>
        </div>

        <div className="px-6 pb-5">
          <button
            onClick={() => setOpen(false)}
            className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold text-sm hover:from-blue-700 hover:to-indigo-700 shadow transition"
          >
            Got it, let's play!
          </button>
        </div>
      </div>
    </div>
  );
}

export function RulesButton() {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="px-3 py-1.5 text-sm font-medium text-blue-100 hover:bg-white/10 hover:text-white rounded-lg transition"
      >
        Rules
      </button>
      {open && <RulesModalInline onClose={() => setOpen(false)} />}
    </>
  );
}

function RulesModalInline({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[85vh] overflow-y-auto">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-t-2xl px-6 py-4 text-white">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-extrabold flex items-center gap-2">🏏 How to Play</h2>
            <button onClick={onClose} className="text-white/70 hover:text-white text-xl">✕</button>
          </div>
        </div>
        <div className="px-6 py-5 space-y-4 text-sm text-gray-700">
          <div>
            <h3 className="font-bold text-gray-900 mb-1">📋 Build Your Team</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600">
              <li>Pick exactly <span className="font-semibold">11 players</span> from the two teams playing</li>
              <li>Stay within the <span className="font-semibold">100 credit budget</span></li>
              <li>Maximum <span className="font-semibold">4 overseas players</span> (marked with ✈️)</li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold text-gray-900 mb-1">👥 Team Composition</h3>
            <p className="text-gray-600">Min 1 WK, 4 BAT, 3 BOWL, 1 AR. Remaining 2 slots are flexible.</p>
          </div>
          <div>
            <h3 className="font-bold text-gray-900 mb-1">🔒 Lockout</h3>
            <p className="text-gray-600">Team locks 1 hour before match start.</p>
          </div>
          <div>
            <h3 className="font-bold text-gray-900 mb-1">🎯 Bonus</h3>
            <p className="text-gray-600">Correct toss prediction = +10 pts. Correct MOTM = +25 pts.</p>
          </div>
        </div>
        <div className="px-6 pb-5">
          <button onClick={onClose} className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold text-sm shadow">
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
}
