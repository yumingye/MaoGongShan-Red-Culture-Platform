import { createApp } from 'vue'
import {
  ElAlert,
  ElBacktop,
  ElBreadcrumb,
  ElBreadcrumbItem,
  ElButton,
  ElCard,
  ElCarousel,
  ElCarouselItem,
  ElCol,
  ElCollapse,
  ElCollapseItem,
  ElDescriptions,
  ElDescriptionsItem,
  ElDropdown,
  ElDropdownItem,
  ElDropdownMenu,
  ElEmpty,
  ElForm,
  ElFormItem,
  ElIcon,
  ElInput,
  ElLink,
  ElLoading,
  ElOption,
  ElPagination,
  ElProgress,
  ElRadioButton,
  ElRadioGroup,
  ElRow,
  ElSegmented,
  ElSelect,
  ElStatistic,
  ElTable,
  ElTableColumn,
  ElTabPane,
  ElTabs,
  ElTag,
  ElTimeline,
  ElTimelineItem,
  ElUpload
} from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import './styles/global.css'

const app = createApp(App)

const elementComponents = [
  ElAlert, ElBacktop, ElBreadcrumb, ElBreadcrumbItem, ElButton, ElCard,
  ElCarousel, ElCarouselItem, ElCol, ElCollapse, ElCollapseItem,
  ElDescriptions, ElDescriptionsItem, ElDropdown, ElDropdownItem,
  ElDropdownMenu, ElEmpty, ElForm, ElFormItem, ElIcon, ElInput, ElLink,
  ElOption, ElPagination, ElProgress, ElRadioButton, ElRadioGroup, ElRow,
  ElSegmented, ElSelect, ElStatistic, ElTable, ElTableColumn, ElTabPane,
  ElTabs, ElTag, ElTimeline, ElTimelineItem, ElUpload
]

for (const component of elementComponents) app.component(component.name, component)

app.use(ElLoading)
app.use(router)
app.mount('#app')
