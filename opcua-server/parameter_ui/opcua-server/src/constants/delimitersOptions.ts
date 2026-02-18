export enum Delimiter {
  COMMA = ",",
  TAB = "\t",
  SEMICOLON = ";",
  SPACE = " ",
  COLON = ":",
  EQUAL = "=",
  SLASH = "/"
}

export const delimitersOptions = [
  { label: "カンマ（,）", value: Delimiter.COMMA },
  { label: "タブ（\t）", value: Delimiter.TAB },
  { label: "セミコロン（;）", value: Delimiter.SEMICOLON },
  { label: "半角スペース（ ）", value: Delimiter.SPACE },
  { label: "コロン（:）", value: Delimiter.COLON },
  { label: "イコール（=）", value: Delimiter.EQUAL },
  { label: "スラッシュ（/）", value: Delimiter.SLASH }
];
