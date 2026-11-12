// T-04 (FR-PRT-01, FR-PRT-02, NFR-USB-01) ตรวจด้วย AC-PRT-01
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { vi } from 'vitest'

import PrintPage from '../pages/PrintPage.jsx'

const MODES = [
  { code: 'BW', label: 'ขาว-ดำ', rate_per_page: 1 },
  { code: 'Color', label: 'สี', rate_per_page: 5 },
]

function makeClient() {
  return {
    uploadPrintFile: vi.fn().mockResolvedValue({ file_id: 'FILE-0001', filename: 'report.pdf', size_bytes: 1258291, pages_detected: null }),
    getPrintOptions: vi.fn().mockImplementation(async ({ pages, copies, colorMode }) => ({
      file_id: 'FILE-0001',
      pages,
      copies,
      color_mode: colorMode,
      allowed_color_modes: MODES,
      total_pages: pages * copies,
      estimated_cost: pages * copies * (colorMode === 'Color' ? 5 : 1),
    })),
  }
}

async function chooseFile(name = 'report.pdf', size = 1258291, type = 'application/pdf') {
  const file = new File(['x'], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  fireEvent.change(screen.getByLabelText('ไฟล์'), { target: { files: [file] } })
}

describe('AC-PRT-01 เห็นตัวเลือกการพิมพ์และค่าใช้บริการก่อนยืนยัน', () => {
  it('AC-PRT-01 เลือกไฟล์ กรอก 12 หน้า 2 ชุด แล้วเห็นบรรทัดคำนวณและค่าใช้บริการ', async () => {
    // Given นักศึกษาเลือกไฟล์ที่รองรับ
    const client = makeClient()
    render(<PrintPage client={client} />)
    await chooseFile()
    expect(await screen.findByText('report.pdf (1.2 MB)')).toBeTruthy()

    // When นักศึกษากำหนดจำนวนหน้าและจำนวนชุด
    fireEvent.change(screen.getByLabelText('จำนวนหน้า'), { target: { value: '12' } })
    fireEvent.change(screen.getByLabelText('จำนวนชุด'), { target: { value: '2' } })

    // Then ระบบแสดงตัวเลือกการพิมพ์และค่าใช้บริการที่คำนวณถูกต้องก่อนให้ยืนยัน
    const cost = within(await screen.findByLabelText('ค่าใช้บริการ'))
    await waitFor(() => expect(cost.getByText('12 หน้า × 2 ชุด = 24 หน้า')).toBeTruthy())
    expect(cost.getByText('24 บาท')).toBeTruthy()
    expect(screen.getByLabelText('ขาว-ดำ')).toBeTruthy()
    fireEvent.click(screen.getByLabelText('สี'))
    await waitFor(() => expect(cost.getByText('120 บาท')).toBeTruthy())
    expect(client.uploadPrintFile).toHaveBeenCalledWith({ filename: 'report.pdf', contentType: 'application/pdf', sizeBytes: 1258291 })
  })
})
