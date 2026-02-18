export enum Round {
  NONE = -1,
  MILLION = 1000000,
  THOUSAND = 1000,
  INTEGER = 0,
  ONE_DECIMAL = 1,
  THREE_DECIMAL = 3,
  SIX_DECIMAL = 6
}

export const roundOptions = [
  { label: "なし", value: Round.NONE },
  { label: "百万", value: Round.MILLION },
  { label: "千", value: Round.THOUSAND },
  { label: "整数", value: Round.INTEGER },
  { label: "小数第一位", value: Round.ONE_DECIMAL },
  { label: "小数第三位", value: Round.THREE_DECIMAL },
  { label: "小数第六位", value: Round.SIX_DECIMAL }
];
