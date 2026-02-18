export enum TsFormat {
  MICRO_SEC = 0,
  MILLI_SEC = 1,
  HUNDRED_MILLI_SEC = 2,
  FIVE_HUNDRED_MILLI_SEC = 3,
  SEC = 4
}

export const tsFormatOptions = [
  { label: "マイクロ秒表示", value: TsFormat.MICRO_SEC },
  { label: "ミリ秒表示", value: TsFormat.MILLI_SEC },
  { label: "100ミリ秒表示", value: TsFormat.HUNDRED_MILLI_SEC },
  { label: "500ミリ秒表示", value: TsFormat.FIVE_HUNDRED_MILLI_SEC },
  { label: "秒表示", value: TsFormat.SEC }
];
