BEGIN;

ALTER TABLE chat_sessions
  ADD COLUMN IF NOT EXISTS title TEXT;

UPDATE chat_sessions
SET title = COALESCE(title, 'Scivly chat session')
WHERE title IS NULL;

ALTER TABLE chat_sessions
  ALTER COLUMN title SET NOT NULL;

COMMIT;
