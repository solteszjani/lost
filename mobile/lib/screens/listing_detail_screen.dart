import 'package:flutter/material.dart';
import '../models/listing.dart';
import '../services/api_service.dart';

class ListingDetailScreen extends StatelessWidget {
  final Listing item;
  const ListingDetailScreen({super.key, required this.item});

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Bejelentés részletei'), actions: [
      IconButton(icon: const Icon(Icons.flag_outlined), onPressed: () async {
        final reason = await showDialog<String>(context: context, builder: (ctx) {
          final c = TextEditingController();
          return AlertDialog(title: const Text('Bejelentés jelentése'), content: TextField(controller: c, decoration: const InputDecoration(hintText: 'Miért jelentésre méltó?')), actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Mégse')),
            FilledButton(onPressed: () => Navigator.pop(ctx, c.text.trim()), child: const Text('Küldés')),
          ]);
        });
        if (reason != null && reason.isNotEmpty) {
          try { await ApiService.reportListing(item.id, reason); if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Köszönjük, megkaptuk a jelentést.'))); }
          catch (_) { if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Nem sikerült elküldeni.'))); }
        }
      }),
    ]),
    body: ListView(padding: const EdgeInsets.all(18), children: [
      Container(height: 190, decoration: BoxDecoration(color: const Color(0xFFE4F4F1), borderRadius: BorderRadius.circular(18)), child: const Icon(Icons.inventory_2_outlined, size: 64, color: Color(0xFF118F80))),
      const SizedBox(height: 18),
      Text(item.title, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
      const SizedBox(height: 8),
      Wrap(spacing: 8, children: [Chip(label: Text(item.kind)), Chip(label: Text(item.category))]),
      const SizedBox(height: 12),
      Text(item.description),
      const Divider(height: 30),
      _line(Icons.place_outlined, 'Helyszín', item.location),
      _line(Icons.calendar_today_outlined, 'Dátum', item.date),
      _line(Icons.contact_mail_outlined, 'Kapcsolat', item.contact),
      const SizedBox(height: 20),
      const Text('Biztonság: a tárgy átadásakor kérj bizonyítékot a tulajdonjogra. Ne küldj pénzt a tárgy visszaszerzéséért.', style: TextStyle(color: Colors.black54)),
    ]),
  );

  Widget _line(IconData icon, String label, String value) => Padding(padding: const EdgeInsets.symmetric(vertical: 7), child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [Icon(icon, size: 20), const SizedBox(width: 10), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(label, style: const TextStyle(fontWeight: FontWeight.w700)), Text(value)]))]));
}
