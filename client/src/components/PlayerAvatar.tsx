import type { PlayerOut } from "../types";

export default function PlayerAvatar({ player, size = 32 }: { player: PlayerOut; size?: number }) {
  if (player.image_url) {
    return (
      <img
        src={player.image_url}
        alt={player.name}
        className="rounded-full object-cover bg-gray-100 shrink-0"
        style={{ width: size, height: size }}
        onError={(e) => {
          (e.target as HTMLImageElement).style.display = "none";
          (e.target as HTMLImageElement).nextElementSibling?.classList.remove("hidden");
        }}
      />
    );
  }

  const initials = player.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div
      className="rounded-full bg-blue-100 text-blue-700 font-semibold flex items-center justify-center shrink-0"
      style={{ width: size, height: size, fontSize: size * 0.4 }}
    >
      {initials}
    </div>
  );
}
