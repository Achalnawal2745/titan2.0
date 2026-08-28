// Feature flag hook
import { useFlag } from '@vercel/flags/react'

export function useFeatureFlag(flagKey: string) {
  const { value, loading } = useFlag(flagKey)
  return { enabled: value, loading }
}

// Usage example
export function NewFeature() {
  const { enabled, loading } = useFeatureFlag('new_feature')
  
  if (loading) return <div>Loading...</div>
  if (!enabled) return null
  
  return <div>New feature content!</div>
}
