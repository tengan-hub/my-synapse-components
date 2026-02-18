<script setup lang="ts">
import { ref, type Ref, reactive, nextTick } from 'vue';
import { QForm, QTable, type QTableProps } from 'quasar';
import { type CustomUiLib } from './customUiLib';
import { Delimiter, delimitersOptions } from './constants/delimitersOptions';
import { NewlineCode, newlineCodeOptions } from './constants/newlineCodeOptions';
import { TsFormat, tsFormatOptions } from './constants/tsFormatOptions';
import { ChFlag, chFlagOptions } from './constants/chFlagOptions';
import { Round, roundOptions } from './constants/roundOptions';
import { useValidationRules } from './utils/validationRules';
import SynapseSelect from './components/ui/SynapseSelect.vue';

const rules = useValidationRules();

const lib: CustomUiLib = (window as any).customUiLib;
const editMode = ref(true);

const inputDataList = ref<string[]>([]);

const parameter = reactive({
  delimiter: Delimiter.COMMA,
  crlf: NewlineCode.LF,
  header: true,
  roundflg: TsFormat.SEC,
  chg_flg: ChFlag.COUNT,
  maxline: 10,
  bom: true,
  colmap: [] as { data_in: string, data_round: Round }[],
  paid_key: '',
});

const paidKeyInput = ref('');
const registedPaidKey = ref(false);

if (lib) {
  lib.onLoad = onLoad;
  lib.onSave = onSave;
}

async function onLoad(editable: boolean, param: any, isNewComponent: boolean, componentId?: string) {
  editMode.value = editable;

  if (param) {
    parameter.delimiter = param.delimiter ?? Delimiter.COMMA;
    parameter.crlf = param.crlf ?? NewlineCode.LF;
    parameter.header = param.header ?? true;
    parameter.roundflg = param.roundflg ?? TsFormat.SEC;
    parameter.chg_flg = param.chg_flg ?? ChFlag.COUNT;
    parameter.maxline = param.maxline ?? 10;
    parameter.bom = param.bom ?? true;
    parameter.colmap = param.colmap ?? [];
    parameter.paid_key = param.paid_key ?? '';
  }

  if (isNewComponent) {
    console.log('Parameter setting for new component instance.');
  } else {
    console.log(`Parameter update for component instance ${componentId}.`);
    if (componentId) {
      const res = await lib.api.runMethod(componentId, 'verify_paid_key_method', parameter);
      registedPaidKey.value = res.result.success ?? false;
      const inportData = await lib.api.getInPortData(componentId);
      for (const item of inportData.data) {
        inputDataList.value.push(`${item.source}:${item.name}`);
      }
    }
  }
}

const formRef = ref() as Ref<QForm>;
async function onSave() {
  await nextTick();
  if (!(await formRef.value.validate())) {
    return null;
  }

  // テーブルで表示されていないページの行に対してもバリデーションを行う
  for (const [idx, val] of parameter.colmap.entries()) {
    if (rules.required(val.data_in) !== true) {
      const targetPage = Math.floor(idx / tablePagenation.value.rowsPerPage) + 1;
      tablePagenation.value.page = targetPage;
      await nextTick();
      qTableRef.value.scrollTo(idx % tablePagenation.value.rowsPerPage, 'center');
      await nextTick();
      await formRef.value.validate();
      return null;
    }
  }

  // paid_keyが入力されていればそれを使い、なければキャッシュを使う
  parameter.paid_key = paidKeyInput.value || parameter.paid_key;

  return parameter;
}

const qTableRef = ref() as Ref<QTable>;
const tablePagenation = ref({ rowsPerPage: 10, page: 1 });

const tableHeader: QTableProps['columns'] = [
  { name: 'data_in', label: '入力データ名 or 固定値 ($ts / $abc / $999 / $NULL)', field: 'data_in', align: 'left', classes: 'input-table-body', headerClasses: 'common-table-header', headerStyle: 'width: 65%' },
  { name: 'data_round', label: '丸め単位', field: 'data_round', align: 'left', classes: 'input-table-body', headerClasses: 'common-table-header', headerStyle: 'width: 25%' },
  { name: 'delete', label: '', field: 'delete', align: 'center', classes: 'input-table-body',  headerClasses: 'common-table-header' }
];

function addRow() {
  parameter.colmap.push({ data_in: '', data_round: Round.NONE });
}

const inputDataListFilter = ref<string[]>([...inputDataList.value]);
function onComponentNameFilter(val: string, update: Function) {
  update(() => {
    if (val === '') {
      inputDataListFilter.value = [...inputDataList.value];
    } else {
      const needle = val.toLowerCase();
      inputDataListFilter.value = inputDataList.value.filter(
        x => x.toLowerCase().includes(needle)
      );
    }
  });
}
</script>

<template>
  <q-form ref="formRef" @validation-error="(ref: any) => ref.$el?.scrollIntoView(false)">
    <div class="row justify-start q-gutter-sm">
      <SynapseSelect
        v-model="parameter.delimiter" class="col-4" label="区切り文字"
        :options="delimitersOptions" :disable="!editMode" :rules="[rules.required]"
      />
      <q-select
        v-model="parameter.crlf" class="col-4" label="改行コード"
        map-options emit-value dense options-dense no-error-icon
        label-color="white" color="blue" style="white-space: nowrap;"
        :options="newlineCodeOptions" :disable="!editMode" :rules="[rules.required]"
      />
      <q-checkbox
        v-model="parameter.header" class="col-3" label="ヘッダを付ける"
        color="blue" label-color="white" dense :disable="!editMode" style="white-space: nowrap;"
      />
    </div>
    <div class="row justify-start q-gutter-sm">
      <q-select
        v-model="parameter.roundflg" class="col-4" label="タイムスタンプフォーマット($ts)"
        map-options emit-value dense options-dense no-error-icon
        label-color="white" color="blue" style="white-space: nowrap;"
        :options="tsFormatOptions" :disable="!editMode" :rules="[rules.required]"
      />
      <div class="row justify-start col-4">
        <q-input
          v-if="parameter.chg_flg === 0" v-model="parameter.maxline" class="col-8" label="切替基準"
          type="text" label-color="white" color="blue" dense no-error-icon :disable="!editMode"
          mask="#####" :rules="[rules.required, rules.range(1, 10000)]"
        />
        <q-input
          v-else v-model="parameter.maxline" class="col-8" label="切替基準"
          type="text" label-color="white" color="blue" dense no-error-icon
          :disable="!editMode"
          mask="####" :rules="[rules.required, rules.range(1, 3600)]"
        />
        <q-select
          v-model="parameter.chg_flg" class="col-4" label=""
          map-options emit-value dense options-dense no-error-icon
          label-color="white" color="blue" style="white-space: nowrap;"
          :options="chFlagOptions" :disable="!editMode" :rules="[rules.required]"
          @update:model-value="(val: ChFlag) => {
            parameter.maxline = val === ChFlag.COUNT
              ? Number(String(parameter.maxline).slice(0, 5))
              : Number(String(parameter.maxline).slice(0, 4))
          }"
        />
      </div>
      <q-checkbox
        v-model="parameter.bom" class="col-3" label="BOMを付ける"
        color="blue" label-color="white" dense :disable="!editMode" style="white-space: nowrap;"
      />
    </div>

    <div>
      <q-table
        v-model:pagination="tablePagenation"
        ref="qTableRef" style="height: 300px;" class="q-py-sm common-table-header-sticky"
        :rows="parameter.colmap" :columns="tableHeader" :row-key="(row: any) => parameter.colmap.indexOf(row)"
        :rows-per-page-options="[10, 100, 1000, 0]"
        table-header-style="background-color: #1d1d1d; user-select: none;" table-style="user-select: none"
        dense flat virtual-scroll
        no-data-label="データなし" rows-per-page-label="ページあたりの件数:"
      >
        <template #header-cell="scope">
          <q-th :props="scope">
            <fieldset :disabled="!editMode" :class="editMode ? 'editable-field' : 'uneditable-field'">
              {{ scope.col.label }}
            </fieldset>
          </q-th>
        </template>

        <template #body-cell-data_in="scope">
          <q-td :props="scope">
            <q-select
              v-model="parameter.colmap[scope.rowIndex]!.data_in"
              :options="inputDataListFilter" :disable="!editMode"
              map-options emit-value dense options-dense no-error-icon
              use-input new-value-mode="add-unique" fill-input hide-selected
              borderless hide-bottom-space input-class="q-py-none" input-debounce="0"
              @filter="onComponentNameFilter" placeholder="Input Data or Fixed Value"
              @blur="(e: any) => parameter.colmap[scope.rowIndex]!.data_in = e.target.value"
              :maxlength="100" :rules="[rules.required]"
            />
          </q-td>
        </template>

        <template #body-cell-data_round="scope">
          <q-td :props="scope">
            <q-select
              v-model="parameter.colmap[scope.rowIndex]!.data_round"
              :options="roundOptions" :disable="!editMode" :rules="[rules.required]"
              map-options emit-value dense options-dense no-error-icon
              borderless hide-bottom-space input-class="q-py-none"
            />
          </q-td>
        </template>

        <template #body-cell-delete="scope">
          <q-td :props="scope">
            <div>
              <q-btn
                size="md" icon="delete" dense flat round :disable="!editMode"
                @click="parameter.colmap.splice(scope.rowIndex, 1)"
              />
            </div>
          </q-td>
        </template>
      </q-table>
      <div class="row justify-center">
        <q-btn
          class="col-12 add_data_list_btn" label="追加"
          size="md" color="white" flat :disable="!editMode" @click="addRow"
        />
      </div>
    </div>
    <div class="row justify-start q-mt-md">
      <q-input
        v-model="paidKeyInput" class="col-12" label="アクティベーションキー" :placeholder="registedPaidKey ? '登録済み' : '未登録もしくは無効なキー'"
        type="text" label-color="white" color="blue" dense no-error-icon :disable="!editMode" stack-label
      />
    </div>
  </q-form>
</template>

<style scoped>
.add_data_list_btn {
  border: dashed 1px white;
}
</style>
