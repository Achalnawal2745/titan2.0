// Welcome email template (Resend + React Email)
import { Html, Head, Body, Container, Text, Button } from '@react-email/components'

export default function WelcomeEmail({ name }: { name: string }) {
  return (
    <Html>
      <Head />
      <Body style={{ fontFamily: 'sans-serif' }}>
        <Container>
          <Text>Hi {name},</Text>
          <Text>Welcome to our platform!</Text>
          <Button href="https://example.com/get-started">
            Get Started
          </Button>
        </Container>
      </Body>
    </Html>
  )
}

// Send email
import { Resend } from 'resend'
const resend = new Resend(process.env.RESEND_API_KEY)

await resend.emails.send({
  from: 'onboarding@example.com',
  to: user.email,
  subject: 'Welcome!',
  react: WelcomeEmail({ name: user.name })
})
