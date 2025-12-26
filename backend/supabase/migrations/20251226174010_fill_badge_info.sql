UPDATE badge_definitions
SET color_scheme = '{"bronze": "#CD7F32", "silver": "#C0C0C0", "gold": "#FFD700"}'
WHERE color_scheme IS NULL OR color_scheme::text != '{"bronze": "#CD7F32", "silver": "#C0C0C0", "gold": "#FFD700"}';

