import argparse
from imapclient import IMAPClient
import ssl
import email
import logging
import sys
from typing import Optional, Set, Tuple

def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """
    Configure logging settings.
    
    Args:
        debug: If True, set log level to DEBUG
        log_file: Optional path to log file. If None, log only to console
    """
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
        
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def connect_to_imap(host: str, username: str, password: str) -> Optional[IMAPClient]:
    """
    Stellt eine Verbindung zum IMAP-Server her.
    
    Args:
        host: IMAP-Server-Hostname
        username: Benutzername
        password: Passwort
        
    Returns:
        IMAPClient-Objekt oder None bei Fehler
    """
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        logger = logging.getLogger(__name__)
        logger.info(f"Verbinde mit IMAP-Server {host}...")
        imap_client = IMAPClient(host, ssl=True, ssl_context=ssl_context)
        imap_client.login(username, password)
        logger.info(f"Erfolgreich verbunden mit {host}")
        return imap_client
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler bei der Verbindung zum IMAP-Server {host}: {str(e)}")
        return None

def get_message_ids(imap_client: IMAPClient, folder: str) -> Set[str]:
    """
    Holt alle Message-IDs aus einem Ordner.
    
    Args:
        imap_client: IMAPClient-Objekt
        folder: Name des Ordners
        
    Returns:
        Set von Message-IDs
    """
    try:
        imap_client.select_folder(folder)
        messages = imap_client.search(['ALL'])
        message_ids = set()
        
        if not messages:
            logger = logging.getLogger(__name__)
            logger.info(f"Keine Nachrichten in Ordner {folder} gefunden")
            return message_ids
            
        logger = logging.getLogger(__name__)
        logger.info(f"Verarbeite {len(messages)} Nachrichten in Ordner {folder}")
        
        for msgid, data in imap_client.fetch(messages, ['RFC822']).items():
            msg = email.message_from_bytes(data[b'RFC822'])
            if msg['Message-ID']:
                message_ids.add(msg['Message-ID'])
                
        return message_ids
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler beim Abrufen der Message-IDs aus Ordner {folder}: {str(e)}")
        return set()

def sync_imap_accounts(
    host1: str, user1: str, password1: str,
    host2: str, user2: str, password2: str,
    dry_run: bool = False
) -> None:
    """
    Synchronisiert zwei IMAP-Konten.
    
    Args:
        host1: Quell-IMAP-Server
        user1: Quell-Benutzername
        password1: Quell-Passwort
        host2: Ziel-IMAP-Server
        user2: Ziel-Benutzername
        password2: Ziel-Passwort
        dry_run: Wenn True, werden keine Änderungen vorgenommen
    """
    imap_client1 = connect_to_imap(host1, user1, password1)
    imap_client2 = connect_to_imap(host2, user2, password2)

    if not (imap_client1 and imap_client2):
        logger = logging.getLogger(__name__)
        logger.error("Konnte nicht zu beiden IMAP-Servern verbinden")
        return

    try:
        folders = imap_client1.list_folders()
        logger = logging.getLogger(__name__)
        logger.info(f"Gefundene Ordner auf {host1}: {len(folders)}")

        for flags, delimiter, folder_name in folders:
            logger = logging.getLogger(__name__)
            logger.info(f"Synchronisiere Ordner: {folder_name}")

            # Prüfe und erstelle Zielordner
            target_folders = [f[2] for f in imap_client2.list_folders()]
            if folder_name not in target_folders:
                if not dry_run:
                    imap_client2.create_folder(folder_name)
                logger = logging.getLogger(__name__)
                logger.info(f"Ordner {folder_name} auf {host2} erstellt")

            # Hole existierende Nachrichten-IDs
            target_message_ids = get_message_ids(imap_client2, folder_name)

            # Synchronisiere Nachrichten
            imap_client1.select_folder(folder_name)
            messages = imap_client1.search(['ALL'])
            
            if not messages:
                logger = logging.getLogger(__name__)
                logger.info(f"Keine Nachrichten in Quellordner {folder_name}")
                continue

            logger = logging.getLogger(__name__)
            logger.info(f"Verarbeite {len(messages)} Nachrichten in {folder_name}")
            
            for msgid, data in imap_client1.fetch(messages, ['RFC822', 'FLAGS']).items():
                msg = email.message_from_bytes(data[b'RFC822'])
                message_id = msg['Message-ID']
                
                if not message_id:
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Nachricht {msgid} hat keine Message-ID")
                    continue
                    
                flags = data[b'FLAGS']

                if message_id not in target_message_ids:
                    if not dry_run:
                        imap_client2.append(folder_name, data[b'RFC822'], flags=flags)
                        logger = logging.getLogger(__name__)
                        logger.info(f"Nachricht {msgid} nach {folder_name} auf {host2} kopiert")
                    else:
                        logger = logging.getLogger(__name__)
                        logger.info(f"[Dry-Run] Würde Nachricht {msgid} nach {folder_name} auf {host2} kopieren")
                else:
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Nachricht {msgid} bereits in {folder_name} auf {host2} vorhanden")

    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Fehler bei der Synchronisation: {str(e)}")
    finally:
        logger = logging.getLogger(__name__)
        logger.info("Schließe IMAP-Verbindungen...")
        imap_client1.logout()
        imap_client2.logout()

def main():
    """Main function for command line execution"""
    parser = argparse.ArgumentParser(description="Synchronize IMAP accounts")
    parser.add_argument('--host1', type=str, help='IMAP host 1 (source)', required=True)
    parser.add_argument('--user1', type=str, help='Username for host 1 (source)', required=True)
    parser.add_argument('--password1', type=str, help='Password for host 1 (source)', required=True)
    parser.add_argument('--host2', type=str, help='IMAP host 2 (target)', required=True)
    parser.add_argument('--user2', type=str, help='Username for host 2 (target)', required=True)
    parser.add_argument('--password2', type=str, help='Password for host 2 (target)', required=True)
    parser.add_argument('--dry-run', action='store_true', help='Perform a trial run with no changes made')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--log-file', type=str, help='Path to log file (optional)', default=None)
    
    args = parser.parse_args()
    
    setup_logging(args.debug, args.log_file)

    sync_imap_accounts(
        args.host1, args.user1, args.password1,
        args.host2, args.user2, args.password2,
        args.dry_run
    )

if __name__ == "__main__":
    main()
