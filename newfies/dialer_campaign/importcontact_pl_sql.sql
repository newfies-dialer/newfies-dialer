CREATE PROCEDURE importcontact_pl_sql(	
	IN campaign_id INT(10),   
	IN phonebook_id INT(10)
) 
BEGIN
	INSERT INTO dialer_campaign_subscriber (contact_id, campaign_id, duplicate_contact, status, created_date, updated_date)
	(SELECT id, campaign_id, contact, 1, NOW(), NOW() FROM dialer_contact WHERE phonebook_id=phonebook_id);
END;
