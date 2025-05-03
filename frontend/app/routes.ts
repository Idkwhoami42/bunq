import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
    index("routes/home.tsx"),
    route("/trip/:id", "routes/trip.tsx"),
    route("/trip/:id/chat", "routes/chat.tsx"),
    route("/trip/:id/pot", "routes/pot.tsx"),
    route("/trip/:id/leaderboard", "routes/leaderboard.tsx"),
    route("/test", "routes/test.tsx"),
] satisfies RouteConfig;
