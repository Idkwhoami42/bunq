import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
    index("routes/home.tsx"),
    route("/chat", "routes/chat.tsx"),
    route("/trip/:id", "routes/trip.tsx")
] satisfies RouteConfig;
