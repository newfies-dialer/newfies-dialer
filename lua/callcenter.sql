CREATE TABLE members (
   queue         VARCHAR(255),
   system        VARCHAR(255),
   uuid      VARCHAR(255) NOT NULL DEFAULT '',
   session_uuid     VARCHAR(255) NOT NULL DEFAULT '',
   cid_number        VARCHAR(255),
   cid_name      VARCHAR(255),
   system_epoch     INTEGER NOT NULL DEFAULT 0,
   joined_epoch     INTEGER NOT NULL DEFAULT 0,
   rejoined_epoch   INTEGER NOT NULL DEFAULT 0,
   bridge_epoch     INTEGER NOT NULL DEFAULT 0,
   abandoned_epoch  INTEGER NOT NULL DEFAULT 0,
   base_score       INTEGER NOT NULL DEFAULT 0,
   skill_score      INTEGER NOT NULL DEFAULT 0,
   serving_agent    VARCHAR(255),
   serving_system   VARCHAR(255),
   state         VARCHAR(255)
);
CREATE TABLE agents (
   name      VARCHAR(255),
   system    VARCHAR(255),
   uuid      VARCHAR(255),
   type      VARCHAR(255),
   contact   VARCHAR(255),
   status    VARCHAR(255),
   state   VARCHAR(255),
   max_no_answer INTEGER NOT NULL DEFAULT 0,
   wrap_up_time INTEGER NOT NULL DEFAULT 0,
   reject_delay_time INTEGER NOT NULL DEFAULT 0,
   busy_delay_time INTEGER NOT NULL DEFAULT 0,
   no_answer_delay_time INTEGER NOT NULL DEFAULT 0,
   last_bridge_start INTEGER NOT NULL DEFAULT 0,
   last_bridge_end INTEGER NOT NULL DEFAULT 0,
   last_offered_call INTEGER NOT NULL DEFAULT 0,
   last_status_change INTEGER NOT NULL DEFAULT 0,
   no_answer_count INTEGER NOT NULL DEFAULT 0,
   calls_answered  INTEGER NOT NULL DEFAULT 0,
   talk_time  INTEGER NOT NULL DEFAULT 0,
   ready_time INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE tiers (
   queue    VARCHAR(255),
   agent    VARCHAR(255),
   state    VARCHAR(255),
   level    INTEGER NOT NULL DEFAULT 1,
   position INTEGER NOT NULL DEFAULT 1
);
