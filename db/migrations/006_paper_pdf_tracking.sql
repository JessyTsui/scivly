ALTER TABLE papers
  ADD COLUMN IF NOT EXISTS pdf_path TEXT;

ALTER TABLE papers
  ADD COLUMN IF NOT EXISTS pdf_status TEXT NOT NULL DEFAULT 'missing';

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'chk_papers_pdf_status'
  ) THEN
    ALTER TABLE papers
      ADD CONSTRAINT chk_papers_pdf_status
      CHECK (pdf_status IN ('missing', 'stored', 'failed'));
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS ix_papers_pdf_status
  ON papers (pdf_status);
