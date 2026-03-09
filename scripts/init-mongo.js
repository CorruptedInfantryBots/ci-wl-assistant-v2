db = db.getSiblingDB('admin');

db.players.insertOne({
    discord_user_id: "1234",
    discord_roles_ids: ["1234"],
    seeding_points: 200,
    steamid64: "76561198000000000",
    latest_seeding_activity: new Date()
});

db.configs.insertOne({
    category: "seeding_tracker",
    config: {
        reward_needed_time: {
            value: 115,
            option: 60000
        }
    }
});
