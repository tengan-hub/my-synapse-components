export const useValidationRules = () => {
  const required = (val?: string | number) =>
    (val != null && typeof (val) === 'string' ? val.length > 0 : true) ||
    '必須項目です。';

  const range = (min: number, max: number) => (val: string) =>
    (!val || (min <= Number(val) && Number(val) <= max)) ||
    `${min} - ${max} の値を入力してください`;

  return {
    required,
    range,
  };
};
