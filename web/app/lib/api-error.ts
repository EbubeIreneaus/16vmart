
export type ApiFormError = {
  message: string
  fields: Record<string, string>
}

type FastApiValidationIssue = {
  loc?: Array<string | number>
  msg?: string
}

type FetchErrorShape = {
  data?: { detail?: unknown }
  response?: { _data?: { detail?: unknown } }
}

const fallbackMessage = 'Internal server error. Please try again later.'

export function getApiFormError(error: unknown): ApiFormError {
  const fetchError = error as FetchErrorShape
  const detail = fetchError?.data?.detail ?? fetchError?.response?._data?.detail

  if (typeof detail === 'string') {
    return { message: detail, fields: {} }
  }

  if (Array.isArray(detail)) {
    const fields = detail.reduce<Record<string, string>>((result, issue: FastApiValidationIssue) => {
      const field = issue.loc?.at(-1)
      if (typeof field === 'string' && issue.msg) result[field] = issue.msg
      return result
    }, {})

    return {
      message: Object.keys(fields).length
        ? 'Please correct the highlighted fields and try again.'
        : 'Please check your details and try again.',
      fields
    }
  }

  return { message: fallbackMessage, fields: {} }
}
