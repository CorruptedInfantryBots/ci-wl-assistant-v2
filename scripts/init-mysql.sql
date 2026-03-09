CREATE DATABASE IF NOT EXISTS squadjsci;
USE squadjsci;

CREATE TABLE IF NOT EXISTS ActivityTracker_PlayerSessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    server INT NOT NULL,
    steamID VARCHAR(255) NOT NULL,
    eosID VARCHAR(255) NOT NULL,
    nickname VARCHAR(255),
    joinTime DATETIME NOT NULL,
    leaveTime DATETIME
);

INSERT INTO ActivityTracker_PlayerSessions (server, steamID, eosID, nickname, joinTime, leaveTime)
VALUES (1, '76561198000000000', '0002123456789', 'DummyPlayer', NOW() - INTERVAL 1 HOUR, NOW());
