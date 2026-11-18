INSERT INTO user_account (name, fullname)
SELECT 'spongebob', 'SpongeBob SquarePants'
WHERE NOT EXISTS (
    SELECT 1 FROM user_account WHERE name = 'spongebob'
);

INSERT INTO user_account (name, fullname)
SELECT 'sandy', 'Sandy Cheeks'
WHERE NOT EXISTS (
    SELECT 1 FROM user_account WHERE name = 'sandy'
);

INSERT INTO user_account (name, fullname)
SELECT 'patrick', 'Patrick Star'
WHERE NOT EXISTS (
    SELECT 1 FROM user_account WHERE name = 'patrick'
);

INSERT INTO user_account (name, fullname)
SELECT 'squidward', NULL
WHERE NOT EXISTS (
    SELECT 1 FROM user_account WHERE name = 'squidward'
);

INSERT INTO address (email_address, user_id)
SELECT 'sandy@example.test', user_account.id
FROM user_account
WHERE user_account.name = 'sandy'
  AND NOT EXISTS (
      SELECT 1 FROM address WHERE email_address = 'sandy@example.test'
  );

INSERT INTO address (email_address, user_id)
SELECT 'spongebob@example.test', user_account.id
FROM user_account
WHERE user_account.name = 'spongebob'
  AND NOT EXISTS (
      SELECT 1 FROM address WHERE email_address = 'spongebob@example.test'
  );
