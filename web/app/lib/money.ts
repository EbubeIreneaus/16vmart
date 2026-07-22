export const toUSD = (amount: number | string | undefined | null): string => {
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
    }).format(Number(amount ?? 0))
}
    