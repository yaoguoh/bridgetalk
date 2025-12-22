import { Database, Eye, ListChecks, ShieldCheck, UploadCloud, Workflow } from 'lucide-react'

const features = [
  {
    name: '一键发布',
    description: '把需求与方案快速同步到协作链路，减少往返沟通。',
    icon: UploadCloud,
  },
  {
    name: '安全合规',
    description: '关键内容可追溯，减少误解与信息遗漏风险。',
    icon: ShieldCheck,
  },
  {
    name: '流程可控',
    description: '明确输入与输出，讨论节奏更稳定。',
    icon: Workflow,
  },
  {
    name: '视角识别',
    description: '自动识别产品与开发视角，降低理解成本。',
    icon: Eye,
  },
  {
    name: '结构化产出',
    description: '补齐边界、依赖与验收标准，方便落地。',
    icon: ListChecks,
  },
  {
    name: '沉淀复用',
    description: '关键信息可复盘与复用，减少重复劳动。',
    icon: Database,
  },
]

export function HomePage() {
  return (
    <div className="mx-auto flex min-h-[calc(100vh-130px)] w-full max-w-7xl flex-col justify-center px-6 py-10 sm:px-10 sm:py-12">
      <div className="w-full">
        <h2 className="text-base/7 font-semibold text-indigo-600">沟通更精准</h2>
        <p className="mt-2 text-3xl font-semibold tracking-tight text-pretty text-gray-900 sm:text-4xl">
          没有统一语言？也能高效对齐。
        </p>
        <p className="mt-6 text-lg/8 text-gray-700">
          BridgeTalk 把需求与技术表达对齐到可执行层，减少误解与返工，让协作更顺畅。
        </p>
      </div>
      <dl className="mt-12 grid w-full grid-cols-1 gap-8 text-base/7 text-gray-600 sm:grid-cols-2 lg:grid-cols-3 lg:gap-x-16">
        {features.map((feature) => (
          <div key={feature.name} className="relative pl-9">
            <dt className="inline font-semibold text-gray-900">
              <feature.icon aria-hidden="true" className="absolute top-1 left-1 size-5 text-indigo-600" />
              {feature.name}
            </dt>{' '}
            <dd className="inline">{feature.description}</dd>
          </div>
        ))}
      </dl>
    </div>
  )
}
