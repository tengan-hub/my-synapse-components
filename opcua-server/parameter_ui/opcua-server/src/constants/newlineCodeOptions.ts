export enum NewlineCode {
  LF = "\n",
  CRLF = "\r\n",
  CR = "\r"
}

export const newlineCodeOptions = [
  { label: "LF（\\n）", value: NewlineCode.LF },
  { label: "CRLF（\\r\\n）", value: NewlineCode.CRLF },
  { label: "CR（\\r）", value: NewlineCode.CR }
];
