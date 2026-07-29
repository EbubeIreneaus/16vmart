
export const useForm = <T extends Record<string, unknown>>(initialForm: T) => {
    const form = ref<T>({...initialForm})

    const reset = () => {
        form.value = initialForm
    }
    return {form, reset}
}