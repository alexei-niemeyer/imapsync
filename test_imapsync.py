import unittest
from unittest.mock import MagicMock, patch
from imapsync import connect_to_imap, get_message_ids, sync_imap_accounts

class TestImapSync(unittest.TestCase):
    def setUp(self):
        self.mock_imap = MagicMock()
        self.mock_message = MagicMock()
        self.mock_message.__getitem__.return_value = 'test-message-id'

    @patch('imapsync.IMAPClient')
    def test_connect_to_imap(self, mock_imap_client):
        mock_imap_client.return_value = self.mock_imap
        
        # Test erfolgreiche Verbindung
        result = connect_to_imap('test.host', 'user', 'pass')
        self.assertIsNotNone(result)
        mock_imap_client.assert_called_once()
        
        # Test fehlgeschlagene Verbindung
        mock_imap_client.side_effect = Exception('Connection failed')
        result = connect_to_imap('test.host', 'user', 'pass')
        self.assertIsNone(result)

    def test_get_message_ids(self):
        self.mock_imap.search.return_value = [1]
        mock_email = MagicMock()
        mock_email.__getitem__.return_value = 'test-message-id'
        
        with patch('email.message_from_bytes', return_value=mock_email):
            self.mock_imap.fetch.return_value = {
                1: {b'RFC822': b'test message content'}
            }
            message_ids = get_message_ids(self.mock_imap, 'INBOX')
            self.assertEqual(message_ids, {'test-message-id'})
            
            # Test leerer Ordner
            self.mock_imap.search.return_value = []
            message_ids = get_message_ids(self.mock_imap, 'INBOX')
            self.assertEqual(message_ids, set())

    @patch('imapsync.connect_to_imap')
    def test_sync_imap_accounts(self, mock_connect):
        # Mock für erfolgreiche Verbindungen
        mock_source = MagicMock()
        mock_target = MagicMock()
        mock_connect.side_effect = [mock_source, mock_target]
        
        # Mock für Ordnerliste
        mock_source.list_folders.return_value = [
            ([], '/', 'INBOX')
        ]
        
        # Mock für Nachrichten
        mock_source.search.return_value = [1]
        mock_source.fetch.return_value = {
            1: {
                b'RFC822': b'test content',
                b'FLAGS': ('\\Seen',)
            }
        }
        
        # Test Synchronisation
        sync_imap_accounts(
            'source.host', 'user1', 'pass1',
            'target.host', 'user2', 'pass2',
            dry_run=True
        )
        
        # Überprüfe, ob die Verbindungen hergestellt wurden
        self.assertEqual(mock_connect.call_count, 2)
        
        # Überprüfe, ob die Ordner aufgelistet wurden
        mock_source.list_folders.assert_called_once()

if __name__ == '__main__':
    unittest.main()
