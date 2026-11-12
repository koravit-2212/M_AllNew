// T-04 (FR-EQP-01, NFR-USB-01) ตรวจด้วย AC-EQP-01
import { fireEvent, render, screen } from '@testing-library/react'
import { vi } from 'vitest'

import EquipmentLoanPage from '../pages/EquipmentLoanPage.jsx'

function makeClient(items) {
  return { listEquipmentTypes: vi.fn().mockResolvedValue({ items }) }
}

describe('AC-EQP-01 นักศึกษาเห็นประเภทอุปกรณ์ที่ยืมได้', () => {
  it('AC-EQP-01 แสดงชื่ออุปกรณ์ จำนวนคงเหลือ และป้ายว่าง ให้เลือก', async () => {
    // Given มีรายการอุปกรณ์ให้บริการในระบบ
    const client = makeClient([
      { equipment_type_id: 'A', name: 'อุปกรณ์ทดสอบ 1', available_count: 3 },
      { equipment_type_id: 'B', name: 'อุปกรณ์ทดสอบ 2', available_count: 1 },
    ])

    // When นักศึกษาเข้าหน้าจอยืมอุปกรณ์
    render(<EquipmentLoanPage client={client} />)

    // Then ระบบแสดงประเภทอุปกรณ์ที่สามารถยืมได้ให้เลือก
    expect(await screen.findByText('อุปกรณ์ทดสอบ 1')).toBeTruthy()
    expect(screen.getByText('อุปกรณ์ทดสอบ 2')).toBeTruthy()
    expect(screen.getByText('คงเหลือ 3')).toBeTruthy()
    expect(screen.getByText('คงเหลือ 1')).toBeTruthy()
    expect(screen.getAllByText('ว่าง')).toHaveLength(2)
    expect(screen.getByText('เลือกอุปกรณ์')).toBeTruthy()
    expect(client.listEquipmentTypes).toHaveBeenCalledTimes(1)

    const option = screen.getByRole('button', { name: /อุปกรณ์ทดสอบ 1/ })
    expect(option.getAttribute('aria-pressed')).toBe('false')
    fireEvent.click(option)
    expect(option.getAttribute('aria-pressed')).toBe('true')
  })
})
