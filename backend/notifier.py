"""
E-Mail-Benachrichtigung für neue Ausschreibungen
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from datetime import datetime

# Lade Umgebungsvariablen
from dotenv import load_dotenv
load_dotenv()


class EmailNotifier:
    """Sendet E-Mail-Benachrichtigungen über neue Ausschreibungen"""
    
    def __init__(self):
        # SMTP-Konfiguration aus Umgebungsvariablen
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.sender_email = os.getenv("SENDER_EMAIL", self.smtp_user)
        self.recipient_email = os.getenv("RECIPIENT_EMAIL", "")
    
    def is_configured(self) -> bool:
        """Prüft ob E-Mail konfiguriert ist"""
        return bool(self.smtp_user and self.smtp_password and self.recipient_email)
    
    def send_new_tenders_notification(self, tenders: List[Dict[str, Any]]) -> bool:
        """
        Sendet eine E-Mail mit neuen Ausschreibungen
        
        Args:
            tenders: Liste der neuen Ausschreibungen
            
        Returns:
            True wenn erfolgreich, False bei Fehler
        """
        if not self.is_configured():
            print("E-Mail nicht konfiguriert. Bitte SMTP-Einstellungen in .env setzen.")
            return False
        
        if not tenders:
            print("Keine neuen Ausschreibungen - keine E-Mail gesendet")
            return True
        
        try:
            # E-Mail erstellen
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🔔 {len(tenders)} neue Ausschreibungen gefunden - {datetime.now().strftime('%d.%m.%Y')}"
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email
            
            # Text-Version
            text_content = self._create_text_content(tenders)
            
            # HTML-Version
            html_content = self._create_html_content(tenders)
            
            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))
            
            # E-Mail senden
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"E-Mail erfolgreich gesendet an {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"Fehler beim E-Mail-Versand: {e}")
            return False
    
    def _create_text_content(self, tenders: List[Dict[str, Any]]) -> str:
        """Erstellt den Text-Inhalt der E-Mail"""
        lines = [
            f"Guten Tag,",
            f"",
            f"es wurden {len(tenders)} neue Ausschreibungen gefunden:",
            f"",
            f"=" * 50,
            f""
        ]
        
        for i, tender in enumerate(tenders, 1):
            lines.extend([
                f"{i}. {tender.get('title', 'Ohne Titel')}",
                f"   Auftraggeber: {tender.get('authority', 'N/A')}",
                f"   Ort: {tender.get('location', 'N/A')}",
                f"   Frist: {tender.get('deadline', 'N/A')}",
                f"   Budget: {tender.get('budget', 'N/A')}",
                f"   Portal: {tender.get('source_portal', 'N/A')}",
                f"   Link: {tender.get('source_url', 'N/A')}",
                f"",
                f"-" * 50,
                f""
            ])
        
        lines.extend([
            f"",
            f"Mit freundlichen Grüßen",
            f"TenderScout AI",
            f"",
            f"---",
            f"Diese E-Mail wurde automatisch generiert."
        ])
        
        return "\n".join(lines)
    
    def _create_html_content(self, tenders: List[Dict[str, Any]]) -> str:
        """Erstellt den HTML-Inhalt der E-Mail"""
        tender_rows = ""
        for tender in tenders:
            tender_rows += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 16px;">
                    <h3 style="margin: 0 0 8px 0; color: #1e293b;">{tender.get('title', 'Ohne Titel')}</h3>
                    <p style="margin: 4px 0; color: #64748b; font-size: 14px;">
                        <strong>Auftraggeber:</strong> {tender.get('authority', 'N/A')}<br>
                        <strong>Ort:</strong> {tender.get('location', 'N/A')}<br>
                        <strong>Frist:</strong> <span style="color: #f97316;">{tender.get('deadline', 'N/A')}</span><br>
                        <strong>Budget:</strong> {tender.get('budget', 'N/A')}<br>
                        <strong>Portal:</strong> {tender.get('source_portal', 'N/A')}
                    </p>
                    <a href="{tender.get('source_url', '#')}" 
                       style="display: inline-block; margin-top: 8px; padding: 8px 16px; 
                              background-color: #3b82f6; color: white; text-decoration: none; 
                              border-radius: 6px; font-size: 14px;">
                        Ausschreibung ansehen →
                    </a>
                </td>
            </tr>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                     background-color: #f8fafc; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; 
                        border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #3b82f6, #8b5cf6); padding: 24px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 24px;">🔔 Neue Ausschreibungen</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0;">
                        {len(tenders)} neue Ausschreibungen gefunden
                    </p>
                </div>
                
                <!-- Content -->
                <div style="padding: 24px;">
                    <p style="color: #475569; margin-bottom: 16px;">
                        Guten Tag,<br><br>
                        folgende neue Ausschreibungen wurden heute gefunden:
                    </p>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        {tender_rows}
                    </table>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f1f5f9; padding: 16px; text-align: center;">
                    <p style="color: #64748b; font-size: 12px; margin: 0;">
                        Diese E-Mail wurde automatisch von TenderScout AI generiert.<br>
                        {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


def send_notification(new_tenders: List[Dict[str, Any]]) -> bool:
    """
    Convenience-Funktion zum Senden von Benachrichtigungen
    
    Args:
        new_tenders: Liste der neuen Ausschreibungen
        
    Returns:
        True wenn erfolgreich
    """
    notifier = EmailNotifier()
    return notifier.send_new_tenders_notification(new_tenders)


if __name__ == "__main__":
    # Test
    test_tenders = [
        {
            "title": "Neubau Gymnasium - Rohbauarbeiten",
            "authority": "Stadt Berlin",
            "location": "Berlin",
            "deadline": "15.06.2024",
            "budget": "2.5 Mio €",
            "source_portal": "ausschreibung.at",
            "source_url": "https://example.com/tender/1"
        }
    ]
    
    send_notification(test_tenders)

