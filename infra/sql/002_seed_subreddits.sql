-- Seed initial curated subreddits for hair, scalp, and related concerns
-- These will be expanded with embeddings when first accessed

INSERT INTO subreddits (name, title, about, quality_score) VALUES
-- Hair and scalp health
('Hair', 'Hair care, styles, and health', 'Everything related to hair care, styling, and health issues', 0.8),
('HaircareScience', 'Evidence-based hair care', 'Scientific approach to hair care and scalp health', 0.9),
('FemaleHairLoss', 'Female hair loss support', 'Support and advice for women experiencing hair loss', 0.85),
('MaleHairLoss', 'Male hair loss and treatments', 'Discussion of male pattern baldness and treatments', 0.85),
('SebDerm', 'Seborrheic dermatitis support', 'Community for those dealing with seborrheic dermatitis', 0.9),

-- Skincare and dermatology
('SkincareAddiction', 'Skincare advice and discussion', 'Evidence-based skincare community', 0.95),
('Dermatology', 'Dermatology questions and advice', 'Professional dermatology advice and discussion', 0.9),
('eczema', 'Eczema support community', 'Support for those dealing with eczema and atopic dermatitis', 0.85),

-- Australian specific
('australia', 'Australia discussion', 'General Australian community and discussion', 0.7),
('AskAnAustralian', 'Questions for Australians', 'Ask Australians about life, products, and culture', 0.75),
('AusSkincare', 'Australian skincare', 'Skincare advice specific to Australian products and climate', 0.85),

-- Health and medical
('AskDocs', 'Medical questions', 'Ask medical professionals questions', 0.8),
('HealthAnxiety', 'Health anxiety support', 'Support for those dealing with health anxiety', 0.75),

-- Product recommendations
('HairProducts', 'Hair product reviews', 'Reviews and recommendations for hair products', 0.7),
('NoPoo', 'No shampoo hair care', 'Alternative hair washing methods', 0.8)

ON CONFLICT (name) DO NOTHING;
