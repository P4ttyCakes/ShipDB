-- Competition System Schema for Supabase PostgreSQL
-- Includes PRIMARY KEY constraints and UUID defaults

CREATE TABLE IF NOT EXISTS "competitions" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "name" TEXT NOT NULL,
  "description" TEXT,
  "start_date" DATE NOT NULL,
  "end_date" DATE NOT NULL,
  "location" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS "participants" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "competition_id" UUID NOT NULL,
  "name" TEXT NOT NULL,
  "email" TEXT NOT NULL,
  "phone" TEXT,
  "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY ("competition_id") REFERENCES "competitions"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "results" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "rank" INTEGER NOT NULL,
  "score" DOUBLE PRECISION NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY ("competition_id") REFERENCES "competitions"("id") ON DELETE CASCADE,
  FOREIGN KEY ("participant_id") REFERENCES "participants"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "leaderboard" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "total_score" DOUBLE PRECISION NOT NULL,
  "rank" INTEGER NOT NULL,
  "updated_at" TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY ("competition_id") REFERENCES "competitions"("id") ON DELETE CASCADE,
  FOREIGN KEY ("participant_id") REFERENCES "participants"("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "media" (
  "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  "competition_id" UUID NOT NULL,
  "participant_id" UUID NOT NULL,
  "type" TEXT NOT NULL,
  "url" TEXT NOT NULL,
  "created_at" TIMESTAMP NOT NULL DEFAULT NOW(),
  FOREIGN KEY ("competition_id") REFERENCES "competitions"("id") ON DELETE CASCADE,
  FOREIGN KEY ("participant_id") REFERENCES "participants"("id") ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_participants_competition_id ON "participants"("competition_id");
CREATE INDEX IF NOT EXISTS idx_results_competition_id ON "results"("competition_id");
CREATE INDEX IF NOT EXISTS idx_results_participant_id ON "results"("participant_id");
CREATE INDEX IF NOT EXISTS idx_leaderboard_competition_id ON "leaderboard"("competition_id");
CREATE INDEX IF NOT EXISTS idx_leaderboard_participant_id ON "leaderboard"("participant_id");
CREATE INDEX IF NOT EXISTS idx_media_competition_id ON "media"("competition_id");
CREATE INDEX IF NOT EXISTS idx_media_participant_id ON "media"("participant_id");

