import Link from "next/link";

import { LegalDraftBanner } from "@/components/legal-draft-banner";

export default function PrivacyPage() {
  return (
    <main className="px-4 py-12">
      <article className="prose prose-slate max-w-3xl mx-auto dark:prose-invert">
        <LegalDraftBanner>
          This is a draft policy under legal review. If you spot anything that doesn&apos;t
          match what you experience using CampusVoice, please email {`gaganganesh098@gmail.com`}.
        </LegalDraftBanner>

        <h1>Privacy Policy</h1>
        <p className="text-sm text-muted-foreground not-prose">Last updated: 2026-05-22</p>

        <h2>1. Who we are</h2>
        <p>
          CampusVoice is operated by {`Gagan Ganesh`}, {`{{OPERATOR_ADDRESS}}`}. Contact:{" "}
          {`gaganganesh098@gmail.com`}. See our <Link href="/impressum">Impressum</Link>.
        </p>

        <h2>2. Data we collect</h2>
        <p>
          <strong>On registration:</strong> email address, hashed password (bcrypt), display name,
          country, university (derived from email domain), program/major (optional), year of
          study (optional), privacy consent timestamp.
        </p>
        <p>
          <strong>On use:</strong> posts, votes, comments, IP address + timestamp for each
          action (kept 90 days), user-agent string.
        </p>
        <p>
          <strong>We do NOT collect:</strong> real name, date of birth, ID documents, payment
          information, location data, phone numbers.
        </p>

        <h2>3. Why we collect it (legal basis — Art. 6 GDPR)</h2>
        <ul>
          <li>
            <strong>Performance of contract (Art. 6(1)(b)):</strong> to provide the service.
          </li>
          <li>
            <strong>Legitimate interest (Art. 6(1)(f)):</strong> to prevent abuse, fraud,
            defamation; to keep logs for security.
          </li>
          <li>
            <strong>Consent (Art. 6(1)(a)):</strong> privacy policy acceptance at signup.
          </li>
        </ul>

        <h2>4. How long we keep it</h2>
        <ul>
          <li>
            <strong>Account:</strong> until you delete it.
          </li>
          <li>
            <strong>Posts and comments:</strong> soft-deleted on request; hard-purged within 30
            days.
          </li>
          <li>
            <strong>IP + audit logs:</strong> 90 days.
          </li>
          <li>
            <strong>Account deletion:</strong> cascades to remove your posts, votes, and
            comments unless legally required to retain (e.g. ongoing legal proceedings).
          </li>
        </ul>

        <h2>5. Who we share it with</h2>
        <ul>
          <li>
            <strong>Hosting:</strong> Railway (deployed in EU region — to confirm before launch).
          </li>
          <li>
            <strong>Email delivery:</strong> {`{{EMAIL_PROVIDER}}`} (placeholder — we&apos;ll add
            details when this is configured).
          </li>
          <li>
            <strong>Authorities:</strong> only when legally compelled by a valid German or EU
            court order.
          </li>
          <li>We do not sell or share data for advertising.</li>
        </ul>

        <h2>6. Your rights under GDPR</h2>
        <ul>
          <li>
            <strong>Right to access (Art. 15):</strong> email {`gaganganesh098@gmail.com`} and we&apos;ll
            send a JSON export within 30 days.
          </li>
          <li>
            <strong>Right to rectification (Art. 16):</strong> edit your profile or email us.
          </li>
          <li>
            <strong>Right to deletion (Art. 17):</strong> delete your account from{" "}
            <Link href="/me">/me</Link>, or email us.
          </li>
          <li>
            <strong>Right to portability (Art. 20):</strong> same JSON export as access.
          </li>
          <li>
            <strong>Right to object (Art. 21):</strong> email us.
          </li>
          <li>
            <strong>Right to lodge a complaint:</strong> with the Berlin data protection
            authority (Berliner Beauftragte für Datenschutz und Informationsfreiheit) —{" "}
            <a
              href="https://www.datenschutz-berlin.de"
              target="_blank"
              rel="noopener noreferrer"
            >
              www.datenschutz-berlin.de
            </a>
            .
          </li>
        </ul>

        <h2>7. Cookies</h2>
        <p>
          We use exactly one cookie: an HTTP-only JWT session cookie for authentication. No
          analytics cookies, no advertising cookies, no third-party cookies.
        </p>

        <h2>8. International transfers</h2>
        <p>
          Data is hosted in the EU. If we ever transfer data outside the EU, we&apos;ll update
          this policy and use Standard Contractual Clauses.
        </p>

        <h2>9. Changes to this policy</h2>
        <p>Material changes will be notified by email at least 14 days in advance.</p>

        <h2>10. Contact</h2>
        <p>
          {`Gagan Ganesh`}, {`{{OPERATOR_ADDRESS}}`}, {`gaganganesh098@gmail.com`}
        </p>
      </article>
    </main>
  );
}
