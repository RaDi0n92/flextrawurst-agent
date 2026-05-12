-- Gedankenwelt: privates Notizbuch pro User, mit Loslassen-Mechanismus
CREATE TABLE IF NOT EXISTS gedankenwelt_eintraege (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id     UUID REFERENCES human_users(id) ON DELETE CASCADE NOT NULL,
  inhalt      TEXT NOT NULL,
  typ         VARCHAR DEFAULT 'privat' CHECK (typ IN ('privat','bereit','losgelassen')),
  blase_id    UUID REFERENCES gedankenblasen(id) ON DELETE SET NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW(),
  meta        JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_gedankenwelt_user_created
  ON gedankenwelt_eintraege (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_gedankenwelt_typ
  ON gedankenwelt_eintraege (typ);
