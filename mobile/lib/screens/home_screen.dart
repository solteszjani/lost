import 'package:flutter/material.dart';
import '../models/listing.dart';
import '../services/api_service.dart';
import 'new_listing_screen.dart';
import 'listing_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String kind = 'Mindegyik';
  String category = 'Összes kategória';
  String query = '';
  final search = TextEditingController();
  late Future<List<Listing>> future;

  @override
  void initState() { super.initState(); _load(); }
  void _load() { future = ApiService.getListings(kind: kind, category: category, query: query); }
  void _refresh() => setState(_load);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Row(children: [Icon(Icons.travel_explore, color: Color(0xFF12A895)), SizedBox(width: 8), Text('Találtam', style: TextStyle(fontWeight: FontWeight.w800))]),
        actions: [IconButton(onPressed: _refresh, icon: const Icon(Icons.refresh))],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final ok = await Navigator.push(context, MaterialPageRoute(builder: (_) => const NewListingScreen()));
          if (ok == true) _refresh();
        },
        icon: const Icon(Icons.add), label: const Text('Bejelentés'),
      ),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 4, 16, 10),
          child: TextField(
            controller: search,
            onChanged: (v) { query = v; _refresh(); },
            decoration: const InputDecoration(prefixIcon: Icon(Icons.search), hintText: 'Mit keresel? Hol láttad?',),
          ),
        ),
        SizedBox(height: 44, child: ListView(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 12), children: [
          _filter('Mindegyik', kind), _filter('Elveszett', kind), _filter('Talált', kind),
        ])),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
          child: DropdownButtonFormField<String>(
            value: category,
            decoration: const InputDecoration(contentPadding: EdgeInsets.symmetric(horizontal: 14, vertical: 4)),
            items: ['Összes kategória','Kulcs','Telefon','Pénztárca','Iratok','Táska','Ékszer','Állat','Ruházat','Egyéb']
              .map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
            onChanged: (v) { if (v != null) setState(() { category = v; _load(); }); },
          ),
        ),
        Expanded(child: FutureBuilder<List<Listing>>(
          future: future,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
            if (snapshot.hasError) return _empty('Nem sikerült csatlakozni a szerverhez. Ellenőrizd az API-címet és indítsd el a backendet.');
            final items = snapshot.data ?? [];
            if (items.isEmpty) return _empty('Még nincs bejelentés. Te lehetsz az első, aki segít!');
            return RefreshIndicator(
              onRefresh: () async => _refresh(),
              child: ListView.builder(padding: const EdgeInsets.fromLTRB(16, 4, 16, 90), itemCount: items.length, itemBuilder: (_, i) => _tile(items[i])),
            );
          },
        )),
      ]),
    );
  }

  Widget _filter(String label, String selected) => Padding(
    padding: const EdgeInsets.symmetric(horizontal: 4),
    child: ChoiceChip(label: Text(label), selected: selected == label, onSelected: (_) => setState(() { kind = label; _load(); })),
  );

  Widget _tile(Listing item) => Card(
    margin: const EdgeInsets.only(bottom: 10),
    child: ListTile(
      contentPadding: const EdgeInsets.all(12),
      leading: Container(width: 54, height: 54, decoration: BoxDecoration(color: const Color(0xFFE4F4F1), borderRadius: BorderRadius.circular(12)), child: Icon(item.kind == 'Elveszett' ? Icons.search : Icons.volunteer_activism, color: const Color(0xFF118F80))),
      title: Text(item.title, style: const TextStyle(fontWeight: FontWeight.w700)),
      subtitle: Padding(padding: const EdgeInsets.only(top: 5), child: Text('${item.kind} • ${item.category}\n${item.location} • ${item.date}', maxLines: 2)),
      trailing: const Icon(Icons.chevron_right),
      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ListingDetailScreen(item: item))),
    ),
  );

  Widget _empty(String text) => Center(child: Padding(padding: const EdgeInsets.all(28), child: Text(text, textAlign: TextAlign.center)));
}
