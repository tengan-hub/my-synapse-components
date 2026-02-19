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
import SynapseInput from './components/ui/SynapseInput.vue';
import SynapseSelect from './components/ui/SynapseSelect.vue';

const rules = useValidationRules();

const lib: CustomUiLib = (window as any).customUiLib;
const editMode = ref(true);

const inputDataList = ref<string[]>([]);

const parameter = reactive({
  endpoint: '',
  server_name: '',
  namespace_uri: '',
  enable_anounymous: false,
  auth_method: [] as string[],
  colmap: [] as { data_in: string, data_round: Round }[],
});

if (lib) {
  lib.onLoad = onLoad;
  lib.onSave = onSave;
}

async function onLoad(editable: boolean, param: any, isNewComponent: boolean, componentId?: string) {
  editMode.value = editable;

  if (param) {
    parameter.endpoint = param.endpoint ?? '';
    parameter.server_name = param.server_name ?? '';
    parameter.namespace_uri = param.namespace_uri ?? '';
    parameter.enable_anounymous = param.enable_anounymous ?? false;
    parameter.auth_method = param.auth_method ?? [];
    parameter.colmap = param.colmap ?? [];
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
      <SynapseInput
        v-model="parameter.server_name" class="col-4" label="サーバ名"
        :disable="!editMode" :rules="[rules.required]"
      />
      <SynapseInput
        v-model="parameter.endpoint" class="col-7" label="エンドポイントURL"
        :disable="!editMode" :rules="[rules.required]" prefix="opc.tcp://"
      />
    </div>

    <div class="row justify-start q-gutter-sm">
      <SynapseInput
        v-model="parameter.namespace_uri" class="col-7" label="Namespace URI"
        :disable="!editMode" :rules="[rules.required]"
      />
    </div>

    <div>
      <SynapseSelect
        v-model="parameter.auth_method" class="col-11" label="認証方式"
        :options="delimitersOptions" :disable="!editMode" :rules="[rules.required]"
        :multiple="true"
      />
    </div>

    <div class="row justify-start q-gutter-sm">
      <q-checkbox
        v-model="parameter.enable_anounymous" class="col-3" label="匿名アクセス許可"
        color="blue" label-color="white" dense :disable="!editMode" style="white-space: nowrap;"
      />
    </div>

    <!-- <div>
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
    </div> -->
  </q-form>
</template>

<style scoped>
.add_data_list_btn {
  border: dashed 1px white;
}
</style>
