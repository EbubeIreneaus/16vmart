import { getApiFormError } from '~/lib/api-error'

export function useGetAPIFormError(initialError?: unknown) {
  const fields = reactive<Record<string, string>>({})
  const message = ref('')

  function clearErrors() {
    message.value = ''
    Object.keys(fields).forEach((key) => delete fields[key])
  }

  function setError(error: unknown) {
    clearErrors()
    const apiError = getApiFormError(error)
    message.value = apiError.message
    Object.assign(fields, apiError.fields)
  }

  if (initialError) setError(initialError)

  return { fields, message, setError, clearErrors }
}
